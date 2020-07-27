"""npm metrics collector."""

from typing import Dict, Tuple

from collector_utilities.type import Entities, Responses, Value
from base_collectors import JSONFileSourceCollector

import json

class NpmDependencies(JSONFileSourceCollector):
    """npm collector for dependencies."""

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        installed_dependencies: Dict[str, Dict[str, str]] = {}
        for response in responses:

            #1325: Don't use response.json since aiohttp warns when the Content-Type of the served JSON is incorrect:
            data = await response.read()
            installed_dependencies.update(json.loads(data))
        entities: Entities = [
            dict(
                key=f'{dependency}@{versions.get("current", "?")}', name=dependency,
                current=versions.get("current", "unknown"), wanted=versions.get("wanted", "unknown"),
                latest=versions.get("latest", "unknown"))
            for dependency, versions in installed_dependencies.items()]
        return str(len(entities)), "100", entities

