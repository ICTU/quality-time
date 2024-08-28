"""npm dependencies collector."""

from typing import TypedDict, cast

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
        key = f'{dependency}@{version.get("current", "?")}'
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
