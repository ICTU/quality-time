"""npm dependencies collector."""

from typing import TypedDict, cast

from packaging.version import InvalidVersion, Version

from base_collectors import JSONFileSourceCollector
from collector_utilities.type import JSON, JSONDict
from model import Entities, Entity


class DependencyVersionInfo(TypedDict):
    """Dependency version information."""

    current: str  # Current version
    dependent: str  # Dependent component, i.e. user of the dependency
    latest: str  # Latest version
    location: str  # Location of the package
    wanted: str  # Wanted version


class NpmDependencies(JSONFileSourceCollector):
    """npm collector for dependencies."""

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Override to parse the dependencies from the JSON."""
        entities = Entities()
        for dependency, version_info in cast(JSONDict, json).items():
            versions = version_info if isinstance(version_info, list) else [version_info]
            for version in versions:
                entities.append(self._create_entity(dependency, version))
        return entities

    def _create_entity(self, dependency: str, version: DependencyVersionInfo) -> Entity:
        """Create an entity for the dependency."""
        key = f"{dependency}@{version.get('current', '?')}"
        name = dependency
        if "dependent" in version:
            key += f"@{version['dependent']}"
            name += f" ({version['dependent']})"
        return Entity(
            key=key,
            name=name,
            current=version.get("current", "unknown"),
            wanted=version.get("wanted", "unknown"),
            latest=version.get("latest", "unknown"),
        )

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether the entity's update type is in the selected updates to include."""
        updates_to_include = self._parameter("updates_to_include")
        try:
            current = Version(entity["current"])
            latest = Version(entity["latest"])
        except InvalidVersion:
            return True  # If versions can't be parsed as semver, don't filter the entity out
        if latest.major > current.major:
            update_type = "major"
        elif latest.minor > current.minor:
            update_type = "minor"
        else:
            update_type = "patch"
        return update_type in updates_to_include
