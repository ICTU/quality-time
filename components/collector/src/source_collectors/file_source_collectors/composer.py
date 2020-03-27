"""Composer metrics collector."""

from typing import Dict, List, Tuple

from collector_utilities.type import Entities, Responses, Value
from base_collectors import JSONFileSourceCollector


class ComposerDependencies(JSONFileSourceCollector):
    """Composer collector for dependencies."""

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        statuses = self._parameter("latest_version_status")
        installed_dependencies: List[Dict[str, str]] = []
        for response in responses:
            installed_dependencies.extend((await response.json()).get("installed", []))
        entities: Entities = [
            dict(
                key=f'{dependency["name"]}@{dependency.get("version", "?")}',
                name=dependency["name"], version=dependency.get("version", "unknown"),
                homepage=dependency.get("homepage", ""), latest=dependency.get("latest", "unknown"),
                latest_status=dependency.get("latest-status", "unknown"),
                description=dependency.get("description", ""), warning=dependency.get("warning", ""))
            for dependency in installed_dependencies if dependency.get("latest-status", "unknown") in statuses]
        return str(len(entities)), str(len(installed_dependencies)), entities
