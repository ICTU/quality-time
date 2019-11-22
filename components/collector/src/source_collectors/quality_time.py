"""Collector for Quality-time."""

from functools import lru_cache
from typing import Dict, Optional
from urllib import parse

from collector_utilities.type import Entities, Response, Responses, URL, Value
from .source_collector import SourceCollector


class QualityTimeMetrics(SourceCollector):
    """Collector to get the "metrics" metric from Quality-time."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__counted_metrics: Optional[Dict[str, Dict]] = None

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
        return str(len(self._parse_source_responses_entities(responses)))

    def _parse_source_responses_total(self, responses: Responses) -> Value:
        return str(len(self.__get_metrics(responses[0])))

    def _parse_source_responses_entities(self, responses: Responses) -> Entities:
        if self.__counted_metrics is None:  # Can't use lru_cache because responses is a list. Cache by hand instead.
            self.__counted_metrics = self.__count_metrics(responses)
        landing_url = self._landing_url(responses)
        entities: Entities = []
        for metric_uuid, metric in self.__counted_metrics.items():
            metric_name = metric.get("name") or self._datamodel["metrics"][metric["type"]]["name"]
            report_url = f"{landing_url}/{metric['report_uuid']}"
            subject_url = f"{report_url}#{metric['subject_uuid']}"
            metric_url = f"{report_url}#{metric_uuid}"
            entities.append(
                dict(
                    key=metric_uuid, report=metric["report_title"], subject=metric["subject_name"], metric=metric_name,
                    report_url=report_url, subject_url=subject_url, metric_url=metric_url, status=metric["status"],
                    target=metric["target"], measurement=metric["measurement"]))
        return entities

    def __count_metrics(self, responses: Responses) -> Dict[str, Dict]:
        """Count the metrics from the responses."""
        measurements_by_metric_uuid = dict()
        for response in responses[1:]:
            if measurements := response.json()["measurements"]:
                last = measurements[-1]
                measurements_by_metric_uuid[last["metric_uuid"]] = last
        status_to_count = self._parameter("status")
        metrics = dict()
        for metric_uuid, metric in self.__get_metrics(responses[0]).items():
            scale = metric.get("scale", "count")
            scale_data = measurements_by_metric_uuid.get(metric_uuid, {}).get(scale, {})
            status = scale_data.get("status")
            if status in status_to_count or (status is None and "unknown" in status_to_count):
                metric["status"] = status
                unit = metric.get("unit") or self._datamodel["metrics"][metric["type"]]["unit"]
                metric["measurement"] = f"{scale_data.get('value') or '?'} {unit}"
                direction = metric.get("direction") or self._datamodel["metrics"][metric["type"]]["direction"]
                direction = {"<": "≦", ">": "≧"}.get(direction, direction)
                target = metric.get("target") or self._datamodel["metrics"][metric["type"]]["target"]
                metric["target"] = f"{direction} {target} {unit}"
                metrics[metric_uuid] = metric
        return metrics

    @lru_cache(maxsize=4)
    def __get_metrics(self, response: Response) -> Dict[str, Dict]:
        """Get the relevant metrics from the reports response."""

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
            for subject_uuid, subject in report.get("subjects", {}).items():
                for metric_uuid, metric in subject.get("metrics", {}).items():
                    if metric_is_to_be_measured(metric, metric_types, source_types, tags):
                        metric["report_title"] = report["title"]
                        metric["subject_name"] = subject["name"]
                        metric["subject_uuid"] = subject_uuid
                        metrics[metric_uuid] = metric
        return metrics
