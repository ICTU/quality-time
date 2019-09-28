"""Pyup.io Safety metrics collector."""

from utilities.type import Entities, Responses, Value
from .source_collector import SourceCollector


class PyupioSafetySecurityWarnings(SourceCollector):
    """Pyup.io Safety collector for security warnings."""
    PACKAGE, AFFECTED, INSTALLED, VULNERABILITY, KEY = range(5)

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(len(responses[0].json()))

    def _parse_source_responses_entities(self, responses: Responses) -> Entities:
        """Return a list of warnings."""
        return [
            dict(key=warning[self.KEY], package=warning[self.PACKAGE], installed=warning[self.INSTALLED],
                 affected=warning[self.AFFECTED], vulnerability=warning[self.VULNERABILITY])
            for warning in responses[0].json()]
