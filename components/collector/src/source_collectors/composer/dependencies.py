"""Composer dependencies collector."""

from base_collectors import JSONFileSourceCollector
from model import Entities, Entity, SourceMeasurement, SourceResponses


class ComposerDependencies(JSONFileSourceCollector):
    """Composer collector for dependencies."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the dependencies."""
        installed_dependencies: list[dict[str, str]] = []
        for response in responses:
            installed_dependencies.extend((await response.json(content_type=None)).get("installed", []))
        entities = [
            Entity(
                key=f'{dependency["name"]}@{dependency.get("version", "?")}',
                name=dependency["name"],
                version=dependency.get("version", "unknown"),
                homepage=dependency.get("homepage", ""),
                latest=dependency.get("latest", "unknown"),
                latest_status=dependency.get("latest-status", "unknown"),
                description=dependency.get("description", ""),
                warning=dependency.get("warning", ""),
            )
            for dependency in installed_dependencies
        ]
        return SourceMeasurement(
            entities=Entities([entity for entity in entities if self._include_entity(entity)]),
            total=str(len(installed_dependencies)),
        )

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to include the entity in the measurement."""
        statuses = self._parameter("latest_version_status")
        return entity["latest_status"] in statuses
