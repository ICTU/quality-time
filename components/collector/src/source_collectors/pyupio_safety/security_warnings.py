"""Pyup.io Safety security warnings collector."""

from typing import Final

from base_collectors import JSONFileSourceCollector
from source_model import Entity, SourceMeasurement, SourceResponses


class PyupioSafetySecurityWarnings(JSONFileSourceCollector):
    """Pyup.io Safety collector for security warnings."""

    PACKAGE: Final[int] = 0
    AFFECTED: Final[int] = 1
    INSTALLED: Final[int] = 2
    VULNERABILITY: Final[int] = 3
    KEY: Final[int] = 4

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the security warnings from the JSON."""
        entities = []
        for response in responses:
            entities.extend(
                [
                    Entity(
                        key=warning[self.KEY],
                        package=warning[self.PACKAGE],
                        installed=warning[self.INSTALLED],
                        affected=warning[self.AFFECTED],
                        vulnerability=warning[self.VULNERABILITY],
                    )
                    for warning in await response.json(content_type=None)
                ]
            )
        return SourceMeasurement(entities=entities)
