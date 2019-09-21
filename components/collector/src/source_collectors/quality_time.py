"""Collector for Quality-time."""

from typing import Iterator, List, Union
from urllib import parse

import requests

from utilities.type import URL, Value
from .source_collector import SourceCollector


class QualityTimeMetrics(SourceCollector):
    """Collector to get the "metrics" metric from Quality-time."""

    def _api_url(self) -> URL:
        parts = parse.urlsplit(super()._api_url())
        netloc = f"{parts.netloc.split(':')[0]}:5001"
        return URL(parse.urlunsplit((parts.scheme, netloc, "", "", "")))

    def _get_source_responses(self, api_url: URL) -> List[requests.Response]:
        # First, get the report(s):
        responses = super()._get_source_responses(URL(f"{api_url}/reports"))
        # Then, add the measurements for each of the applicable metrics:
        for metric_uuid in self.__get_metric_uuids(responses[0]):
            responses.extend(super()._get_source_responses(URL(f"{api_url}/measurements/{metric_uuid}")))
        return responses

    def __get_metric_uuids(self, response: requests.Response) -> Iterator[str]:
        """Get the relevant metric uuids from the reports response."""
        report_titles_or_ids = set(self._parameter("reports"))
        tags_to_count = set(self._parameter("tags"))
        for report in response.json()["reports"]:
            if report_titles_or_ids and (report_titles_or_ids & {report["title"], report["report_uuid"]} == set()):
                continue
            for subject in report.get("subjects", {}).values():
                for metric_uuid, metric in subject.get("metrics", {}).items():
                    if tags_to_count and (tags_to_count & set(metric.get("tags", {})) == set()):
                        continue
                    yield metric_uuid

    def _parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        measurements_by_metric_uuid = dict()
        for response in responses[1:]:
            measurements = response.json()["measurements"]
            if measurements:
                last = measurements[-1]
                measurements_by_metric_uuid[last["metric_uuid"]] = last
        status_to_count = self._parameter("status")
        count = 0
        for metric_uuid in self.__get_metric_uuids(responses[0]):
            status = measurements_by_metric_uuid.get(metric_uuid, {}).get("status")
            if status in status_to_count or (status is None and "unknown" in status_to_count):
                count += 1
        return str(count)

    def _parse_source_responses_total(self, responses: List[requests.Response]) -> Value:
        return str(len(list(self.__get_metric_uuids(responses[0]))))

    metric_status_map = {
        "target met (green)": "target_met", "target not met (red)": "target_not_met",
        "near target met (yellow)": "near_target_met", "technical debt target met (grey)": "debt_target_met",
        "unknown (white)": "unknown"}

    def _parameter(self, parameter_key: str) -> Union[str, List[str]]:
        # Override to map the human-readable status indicators to the values used internally
        values = super()._parameter(parameter_key)
        return [self.metric_status_map[value] for value in list(values)] if parameter_key == "status" else values
