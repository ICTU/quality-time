"""Pyup.io Safety security warnings collector."""

from typing import Final

from base_collectors import JSONFileSourceCollector
from source_model import Entities, Entity, SourceResponses


class PyupioSafetySecurityWarnings(JSONFileSourceCollector):
    """Pyup.io Safety collector for security warnings."""

    PACKAGE: Final[int] = 0
    AFFECTED: Final[int] = 1
    INSTALLED: Final[int] = 2
    VULNERABILITY: Final[int] = 3
    KEY: Final[int] = 4

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the security warnings from the JSON."""
        entities = Entities()
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
        return entities
