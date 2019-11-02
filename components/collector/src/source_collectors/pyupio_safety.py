"""Pyup.io Safety metrics collector."""

from collector_utilities.type import Entities, Responses, Value
from .source_collector import FileSourceCollector


class PyupioSafetySecurityWarnings(FileSourceCollector):
    """Pyup.io Safety collector for security warnings."""

    PACKAGE, AFFECTED, INSTALLED, VULNERABILITY, KEY = range(5)
    file_extensions = ["json"]

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(sum(len(response.json()) for response in responses))

    def _parse_source_responses_entities(self, responses: Responses) -> Entities:
        """Return a list of warnings."""
        entities = []
        for response in responses:
            entities.extend(
                [dict(
                    key=warning[self.KEY], package=warning[self.PACKAGE], installed=warning[self.INSTALLED],
                    affected=warning[self.AFFECTED], vulnerability=warning[self.VULNERABILITY])
                 for warning in response.json()])
        return entities
