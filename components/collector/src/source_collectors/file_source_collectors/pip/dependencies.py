"""pip dependencies collector."""

from typing import Dict, List

from base_collectors import JSONFileSourceCollector
from source_model import Entity, SourceMeasurement, SourceResponses


class PipDependencies(JSONFileSourceCollector):
    """pip collector for dependencies."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the dependencies from the JSON."""
        installed_dependencies: List[Dict[str, str]] = []
        for response in responses:
            installed_dependencies.extend(await response.json(content_type=None))
        entities = [
            Entity(
                key=f'{dependency["name"]}@{dependency.get("version", "?")}',
                name=dependency["name"],
                version=dependency.get("version", "unknown"),
                latest=dependency.get("latest_version", "unknown"),
            )
            for dependency in installed_dependencies
        ]
        return SourceMeasurement(entities=entities)
