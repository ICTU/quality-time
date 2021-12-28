"""npm dependencies collector."""

from typing import cast

from base_collectors import JSONFileSourceCollector
from collector_utilities.type import JSON, JSONDict
from model import Entities, Entity


class NpmDependencies(JSONFileSourceCollector):
    """npm collector for dependencies."""

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Override to parse the dependencies from the JSON."""
        return Entities(
            Entity(
                key=f'{dependency}@{versions.get("current", "?")}',
                name=dependency,
                current=versions.get("current", "unknown"),
                wanted=versions.get("wanted", "unknown"),
                latest=versions.get("latest", "unknown"),
            )
            for dependency, versions in cast(JSONDict, json).items()
        )
