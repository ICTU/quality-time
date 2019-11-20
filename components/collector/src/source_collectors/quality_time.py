"""Collector for Quality-time."""

from functools import lru_cache
from typing import Dict
from urllib import parse

from collector_utilities.type import Response, Responses, URL, Value
from .source_collector import SourceCollector


class QualityTimeMetrics(SourceCollector):
    """Collector to get the "metrics" metric from Quality-time."""

    def _api_url(self) -> URL:
        parts = parse.urlsplit(super()._api_url())
        netloc = f"{parts.netloc.split(':')[0]}"
        return URL(parse.urlunsplit((parts.scheme, netloc, "/api/v1", "", "")))

    def _get_source_responses(self, api_url: URL) -> Responses:
        # First, get the report(s):
        responses = super()._get_source_responses(URL(f"{api_url}/reports"))
        # Then, add the measurements for each of the applicable metrics:
        for metric_uuid in self.__get_metrics(responses[0]):
            responses.extend(super()._get_source_responses(URL(f"{api_url}/measurements/{metric_uuid}")))
        return responses

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        measurements_by_metric_uuid = dict()
        for response in responses[1:]:
            if measurements := response.json()["measurements"]:
                last = measurements[-1]
                measurements_by_metric_uuid[last["metric_uuid"]] = last
        status_to_count = self._parameter("status")
        count = 0
        for metric_uuid, metric in self.__get_metrics(responses[0]).items():
            scale = metric.get("scale", "count")
            status = measurements_by_metric_uuid.get(metric_uuid, {}).get(scale, {}).get("status")
            if status in status_to_count or (status is None and "unknown" in status_to_count):
                count += 1
        return str(count)

    def _parse_source_responses_total(self, responses: Responses) -> Value:
        return str(len(self.__get_metrics(responses[0])))

    @lru_cache(maxsize=4)
    def __get_metrics(self, response: Response) -> Dict[str, Dict]:
        """Get the relevant metric uuids from the reports response."""

        def metric_is_to_be_measured(metric, metric_types, source_types, tags) -> bool:
            """Return whether the metric has been selected by the user by means of metric type, source type or tag."""
            if tags and (tags & set(metric.get("tags", {}))) == set():
                return False
            if metric_types and metric["type"] not in metric_types:
                return False
            metric_source_types = {source["type"] for source in metric.get("sources", {}).values()}
            return not (source_types and (source_types & metric_source_types) == set())

        report_titles_or_ids = set(self._parameter("reports"))
        tags = set(self._parameter("tags"))
        metric_types = self._parameter("metric_type")
        source_types = set(self._parameter("source_type"))
        metrics = dict()
        for report in response.json()["reports"]:
            if report_titles_or_ids and (report_titles_or_ids & {report["title"], report["report_uuid"]} == set()):
                continue
            for subject in report.get("subjects", {}).values():
                for metric_uuid, metric in subject.get("metrics", {}).items():
                    if metric_is_to_be_measured(metric, metric_types, source_types, tags):
                        metrics[metric_uuid] = metric
        return metrics
