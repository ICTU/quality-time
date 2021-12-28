"""Bandit security warnings collector."""

from typing import cast

from base_collectors import JSONFileSourceCollector
from collector_utilities.type import JSON, JSONDict
from model import Entities, Entity


class BanditSecurityWarnings(JSONFileSourceCollector):
    """Bandit collector for security warnings."""

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Override to parse the security warnings."""
        severities = self._parameter("severities")
        confidence_levels = self._parameter("confidence_levels")
        return Entities(
            [
                Entity(
                    key=f'{warning["test_id"]}:{warning["filename"]}:{warning["line_number"]}',
                    location=f'{warning["filename"]}:{warning["line_number"]}',
                    issue_text=warning["issue_text"],
                    issue_severity=warning["issue_severity"].capitalize(),
                    issue_confidence=warning["issue_confidence"].capitalize(),
                    more_info=warning["more_info"],
                )
                for warning in cast(JSONDict, json).get("results", [])
                if warning["issue_severity"].lower() in severities
                and warning["issue_confidence"].lower() in confidence_levels
            ]
        )
