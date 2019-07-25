"""Bandit metrics collector."""

from typing import List

from dateutil.parser import parse
import requests

from utilities.type import Entities, Value
from utilities.functions import days_ago
from .source_collector import SourceCollector


class BanditSecurityWarnings(SourceCollector):
    """Bandit collector for security warnings."""

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        return str(len(self.parse_source_responses_entities(responses)))

    def parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        """Return a list of warnings."""
        severities = self.parameter("severities")
        confidence_levels = self.parameter("confidence_levels")
        return [
            dict(
                key=f'{warning["test_id"]}:{warning["filename"]}:{warning["line_number"]}',
                location=f'{warning["filename"]}:{warning["line_number"]}',
                issue_text=warning["issue_text"],
                issue_severity=warning["issue_severity"].capitalize(),
                issue_confidence=warning["issue_confidence"].capitalize(),
                more_info=warning["more_info"])
            for warning in responses[0].json().get("results", []) if warning["issue_severity"].lower() in severities
            and warning["issue_confidence"].lower() in confidence_levels]


class BanditSourceUpToDateness(SourceCollector):
    """Bandit collector for source up-to-dateness."""

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        return str(days_ago(parse(responses[0].json()["generated_at"])))
