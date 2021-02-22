"""npm dependencies collector."""

from base_collectors import JSONFileSourceCollector
from source_model import Entity, SourceMeasurement, SourceResponses


class NpmDependencies(JSONFileSourceCollector):
    """npm collector for dependencies."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the dependencies from the JSOM."""
        installed_dependencies: dict[str, dict[str, str]] = {}
        for response in responses:
            installed_dependencies.update(await response.json(content_type=None))
        entities = [
            Entity(
                key=f'{dependency}@{versions.get("current", "?")}',
                name=dependency,
                current=versions.get("current", "unknown"),
                wanted=versions.get("wanted", "unknown"),
                latest=versions.get("latest", "unknown"),
            )
            for dependency, versions in installed_dependencies.items()
        ]
        return SourceMeasurement(entities=entities)
