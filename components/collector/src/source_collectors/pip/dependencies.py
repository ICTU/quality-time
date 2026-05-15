"""pip dependencies collector."""

from typing import TYPE_CHECKING, TypedDict, cast

from packaging.version import InvalidVersion, Version

from base_collectors import JSONFileSourceCollector
from collector_utilities.functions import version_update
from model import Entities, Entity

if TYPE_CHECKING:
    from collector_utilities.type import JSON


class DependencyVersionInfo(TypedDict):
    """Dependency version information as produced by `pip list --outdated --format json`."""

    name: str
    version: str  # Current version
    latest_version: str  # Latest available version


class PipDependencies(JSONFileSourceCollector):
    """pip collector for dependencies."""

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Override to parse the dependencies from the JSON."""
        return Entities(self._create_entity(dependency) for dependency in cast(list[DependencyVersionInfo], json))

    def _create_entity(self, dependency: DependencyVersionInfo) -> Entity:
        """Create an entity for the dependency."""
        return Entity(
            key=f"{dependency['name']}@{dependency.get('version', '?')}",
            name=dependency["name"],
            version=dependency.get("version", "unknown"),
            latest=dependency.get("latest_version", "unknown"),
        )

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether the entity's update type is in the selected updates to include."""
        try:
            current = Version(entity["version"])
            latest = Version(entity["latest"])
        except InvalidVersion:
            return True  # If versions can't be parsed as semver, don't filter the entity out
        return version_update(latest, current) in self._parameter("updates_to_include")
