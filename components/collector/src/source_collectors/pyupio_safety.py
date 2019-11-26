"""Pyup.io Safety metrics collector."""

from typing import Tuple

from collector_utilities.type import Entities, Responses, Value
from .source_collector import FileSourceCollector


class PyupioSafetySecurityWarnings(FileSourceCollector):
    """Pyup.io Safety collector for security warnings."""

    PACKAGE, AFFECTED, INSTALLED, VULNERABILITY, KEY = range(5)
    file_extensions = ["json"]

    def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        """Return a list of warnings."""
        entities = []
        for response in responses:
            entities.extend(
                [dict(
                    key=warning[self.KEY], package=warning[self.PACKAGE], installed=warning[self.INSTALLED],
                    affected=warning[self.AFFECTED], vulnerability=warning[self.VULNERABILITY])
                 for warning in response.json()])
        return str(len(entities)), "100", entities
