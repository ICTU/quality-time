"""npm metrics collector."""

from typing import Dict

from collector_utilities.type import Entities, Responses
from base_collectors import JSONFileSourceCollector, SourceMeasurement


class NpmDependencies(JSONFileSourceCollector):
    """npm collector for dependencies."""

    async def _parse_source_responses(self, responses: Responses) -> SourceMeasurement:
        installed_dependencies: Dict[str, Dict[str, str]] = {}
        for response in responses:
            installed_dependencies.update(await response.json(content_type=None))
        entities: Entities = [
            dict(
                key=f'{dependency}@{versions.get("current", "?")}', name=dependency,
                current=versions.get("current", "unknown"), wanted=versions.get("wanted", "unknown"),
                latest=versions.get("latest", "unknown"))
            for dependency, versions in installed_dependencies.items()]
        return SourceMeasurement(value=str(len(entities)), entities=entities)
