"""Collector for Quality-time."""

from typing import List
import urllib

import requests

from utilities.type import Value, URL
from .source_collector import SourceCollector


class QualityTimeMetrics(SourceCollector):
    """Collector to get the "metrics" metric from Quality-time."""

    def api_url(self) -> URL:
        parts = urllib.parse.urlsplit(super().api_url())
        netloc = f"{parts.netloc.split(':')[0]}:5001"
        return URL(urllib.parse.urlunsplit((parts.scheme, netloc, "", "", "")))

    def get_source_responses(self, api_url: URL) -> List[requests.Response]:
        responses = super().get_source_responses(f"{api_url}/reports")
        report_title_or_id = self.parameter("report")
        for report in responses[0].json()["reports"]:
            if report_title_or_id and report_title_or_id not in (report["title"], report["report_uuid"]):
                continue
            for subject in report.get("subjects", {}).values():
                for metric_uuid in subject.get("metrics", {}):
                    responses.extend(super().get_source_responses(f"{api_url}/measurements/{metric_uuid}"))
        return responses

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        reports = responses[0].json()["reports"]
        measurements_by_metric_uuid = dict()
        for response in responses[1:]:
            measurements = response.json()["measurements"]
            if measurements:
                last = measurements[-1]
                measurements_by_metric_uuid[last["metric_uuid"]] = last
        print(measurements_by_metric_uuid)
        report_title_or_id = self.parameter("report")
        status_to_count = self.parameter("status")
        count = 0
        for report in reports:
            if report_title_or_id and report_title_or_id not in (report["title"], report["report_uuid"]):
                continue
            for subject in report.get("subjects", {}).values():
                for metric_uuid, metric in subject.get("metrics", {}).items():
                    status = measurements_by_metric_uuid[metric_uuid]["status"] if measurements_by_metric_uuid[metric_uuid] else None
                    if status in status_to_count or (status is None and "unknown" in status_to_count):
                        count += 1
        return str(count)
