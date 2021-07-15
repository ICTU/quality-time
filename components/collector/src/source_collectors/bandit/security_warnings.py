"""Bandit security warnings collector."""

from base_collectors import JSONFileSourceCollector
from model import Entities, Entity, SourceResponses


class BanditSecurityWarnings(JSONFileSourceCollector):
    """Bandit collector for security warnings."""

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the security warnings."""
        severities = self._parameter("severities")
        confidence_levels = self._parameter("confidence_levels")
        entities = Entities()
        for response in responses:
            entities.extend(
                [
                    Entity(
                        key=f'{warning["test_id"]}:{warning["filename"]}:{warning["line_number"]}',
                        location=f'{warning["filename"]}:{warning["line_number"]}',
                        issue_text=warning["issue_text"],
                        issue_severity=warning["issue_severity"].capitalize(),
                        issue_confidence=warning["issue_confidence"].capitalize(),
                        more_info=warning["more_info"],
                    )
                    for warning in (await response.json(content_type=None)).get("results", [])
                    if warning["issue_severity"].lower() in severities
                    and warning["issue_confidence"].lower() in confidence_levels
                ]
            )
        return entities
