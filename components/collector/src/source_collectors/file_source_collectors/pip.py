"""pip metrics collector."""

from typing import Dict, List

from collector_utilities.type import Entities
from base_collectors import JSONFileSourceCollector, SourceMeasurement, SourceResponses


class PipDependencies(JSONFileSourceCollector):
    """pip collector for dependencies."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        installed_dependencies: List[Dict[str, str]] = []
        for response in responses:
            installed_dependencies.extend(await response.json(content_type=None))
        entities: Entities = [
            dict(
                key=f'{dependency["name"]}@{dependency.get("version", "?")}',
                name=dependency["name"], version=dependency.get("version", "unknown"),
                latest=dependency.get("latest_version", "unknown"))
            for dependency in installed_dependencies]
        return SourceMeasurement(entities=entities)
