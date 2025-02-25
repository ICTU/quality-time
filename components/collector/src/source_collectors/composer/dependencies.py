"""Composer dependencies collector."""

from typing import cast

from base_collectors import JSONFileSourceCollector
from collector_utilities.type import JSON, JSONDict
from model import Entities, Entity


class ComposerDependencies(JSONFileSourceCollector):
    """Composer collector for dependencies."""

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Parse the entities from the JSON."""
        return Entities(
            [
                Entity(
                    key=f"{dependency['name']}@{dependency.get('version', '?')}",
                    name=dependency["name"],
                    version=dependency.get("version", "unknown"),
                    homepage=dependency.get("homepage", ""),
                    latest=dependency.get("latest", "unknown"),
                    latest_status=dependency.get("latest-status", "unknown"),
                    description=dependency.get("description", ""),
                    warning=dependency.get("warning", ""),
                )
                for dependency in cast(JSONDict, json).get("installed", [])
            ]
        )

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to include the entity in the measurement."""
        statuses = self._parameter("latest_version_status")
        return entity["latest_status"] in statuses
