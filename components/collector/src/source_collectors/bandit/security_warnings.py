"""Bandit security warnings collector."""

from typing import cast

from base_collectors import JSONFileSourceCollector, SecurityWarningsSourceCollector
from collector_utilities.type import JSON, JSONDict
from model import Entities, Entity


class BanditSecurityWarnings(SecurityWarningsSourceCollector, JSONFileSourceCollector):
    """Bandit collector for security warnings."""

    ENTITY_SEVERITY_ATTRIBUTE = "issue_severity"
    MAKE_ENTITY_SEVERITY_VALUE_LOWER_CASE = True

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Override to parse the security warnings."""
        return Entities(
            [
                Entity(
                    key=f"{warning['test_id']}:{warning['filename']}:{warning['line_number']}",
                    location=f"{warning['filename']}:{warning['line_number']}",
                    issue_text=warning["issue_text"],
                    issue_severity=warning["issue_severity"].capitalize(),
                    issue_confidence=warning["issue_confidence"].capitalize(),
                    more_info=warning["more_info"],
                )
                for warning in cast(JSONDict, json).get("results", [])
            ],
        )

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to include the warning in the measurement."""
        return super()._include_entity(entity) and self.__entity_has_configured_confidence_level(entity)

    def __entity_has_configured_confidence_level(self, entity: Entity) -> bool:
        """Return whether the entity has one of the configured confidence levels."""
        return entity["issue_confidence"].lower() in self._parameter("confidence_levels")
