"""pip dependencies collector."""

from typing import cast

from base_collectors import JSONFileSourceCollector
from collector_utilities.type import JSON, JSONList
from model import Entities, Entity


class PipDependencies(JSONFileSourceCollector):
    """pip collector for dependencies."""

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Override to parse the dependencies from the JSON."""
        return Entities(
            Entity(
                key=f'{dependency["name"]}@{dependency.get("version", "?")}',
                name=dependency["name"],
                version=dependency.get("version", "unknown"),
                latest=dependency.get("latest_version", "unknown"),
            )
            for dependency in cast(JSONList, json)
        )
