"""pip metrics collector."""

from typing import Dict, List, Tuple

from collector_utilities.type import Entities, Responses, Value
from base_collectors import JSONFileSourceCollector


class PipDependencies(JSONFileSourceCollector):
    """pip collector for dependencies."""

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        installed_dependencies: List[Dict[str, str]] = []
        for response in responses:
            installed_dependencies.extend(await response.json(content_type=None))
        entities: Entities = [
            dict(
                key=f'{dependency["name"]}@{dependency.get("version", "?")}',
                name=dependency["name"], version=dependency.get("version", "unknown"),
                latest=dependency.get("latest_version", "unknown"))
            for dependency in installed_dependencies]
        return str(len(entities)), "100", entities
