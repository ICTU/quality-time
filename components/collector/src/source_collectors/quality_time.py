"""Collector for Quality-time."""

from typing import Iterator, List
import urllib

import requests

from utilities.type import URL, Value
from .source_collector import SourceCollector


class QualityTimeMetrics(SourceCollector):
    """Collector to get the "metrics" metric from Quality-time."""

    def api_url(self) -> URL:
        parts = urllib.parse.urlsplit(super().api_url())
        netloc = f"{parts.netloc.split(':')[0]}:5001"
        return URL(urllib.parse.urlunsplit((parts.scheme, netloc, "", "", "")))

    def get_source_responses(self, api_url: URL) -> List[requests.Response]:
        responses = super().get_source_responses(URL(f"{api_url}/reports"))
        for metric_uuid in self.get_metric_uuids(responses[0]):
            responses.extend(super().get_source_responses(URL(f"{api_url}/measurements/{metric_uuid}")))
        return responses

    def get_metric_uuids(self, response: requests.Response) -> Iterator[str]:
        """Get the relevant metric uuids from the reports response."""
        report_titles_or_ids = set(self.parameter("reports"))
        tags_to_count = set(self.parameter("tags"))
        for report in response.json()["reports"]:
            if report_titles_or_ids and (report_titles_or_ids & {report["title"], report["report_uuid"]} == set()):
                continue
            for subject in report.get("subjects", {}).values():
                for metric_uuid, metric in subject.get("metrics", {}).items():
                    if tags_to_count and (tags_to_count & set(metric.get("tags", {})) == set()):
                        continue
                    yield metric_uuid

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        measurements_by_metric_uuid = dict()
        for response in responses[1:]:
            measurements = response.json()["measurements"]
            if measurements:
                last = measurements[-1]
                measurements_by_metric_uuid[last["metric_uuid"]] = last
        status_to_count = self.parameter("status")
        count = 0
        for metric_uuid in self.get_metric_uuids(responses[0]):
            status = measurements_by_metric_uuid.get(metric_uuid, {}).get("status")
            if status in status_to_count or (status is None and "unknown" in status_to_count):
                count += 1
        return str(count)
