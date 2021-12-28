"""Pyup.io Safety security warnings collector."""

from typing import cast, Final

from base_collectors import JSONFileSourceCollector
from collector_utilities.type import JSON
from model import Entities, Entity


JSONSafety = list[list[str]]


class PyupioSafetySecurityWarnings(JSONFileSourceCollector):
    """Pyup.io Safety collector for security warnings."""

    PACKAGE: Final[int] = 0
    AFFECTED: Final[int] = 1
    INSTALLED: Final[int] = 2
    VULNERABILITY: Final[int] = 3
    KEY: Final[int] = 4

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Override to parse the security warnings from the JSON."""
        return Entities(
            [
                Entity(
                    key=warning[self.KEY],
                    package=warning[self.PACKAGE],
                    installed=warning[self.INSTALLED],
                    affected=warning[self.AFFECTED],
                    vulnerability=warning[self.VULNERABILITY],
                )
                for warning in cast(JSONSafety, json)
            ]
        )
