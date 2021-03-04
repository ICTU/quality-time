"""pip dependencies collector."""

from base_collectors import JSONFileSourceCollector
from source_model import Entities, Entity, SourceResponses


class PipDependencies(JSONFileSourceCollector):
    """pip collector for dependencies."""

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the dependencies from the JSON."""
        installed_dependencies: list[dict[str, str]] = []
        for response in responses:
            installed_dependencies.extend(await response.json(content_type=None))
        return Entities(
            Entity(
                key=f'{dependency["name"]}@{dependency.get("version", "?")}',
                name=dependency["name"],
                version=dependency.get("version", "unknown"),
                latest=dependency.get("latest_version", "unknown"),
            )
            for dependency in installed_dependencies
        )
