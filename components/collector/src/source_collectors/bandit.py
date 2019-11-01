"""Bandit metrics collector."""

from dateutil.parser import parse

from collector_utilities.type import Entities, Responses, Value
from collector_utilities.functions import days_ago
from .source_collector import SourceCollector


class BanditSecurityWarnings(SourceCollector):
    """Bandit collector for security warnings."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(len(self._parse_source_responses_entities(responses)))

    def _parse_source_responses_entities(self, responses: Responses) -> Entities:
        """Return a list of warnings."""
        severities = self._parameter("severities")
        confidence_levels = self._parameter("confidence_levels")
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

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(days_ago(parse(responses[0].json()["generated_at"])))
