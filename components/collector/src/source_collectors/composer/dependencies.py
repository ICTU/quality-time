"""Composer dependencies collector."""

from typing import Dict, List

from base_collectors import JSONFileSourceCollector
from source_model import Entity, SourceMeasurement, SourceResponses


class ComposerDependencies(JSONFileSourceCollector):
    """Composer collector for dependencies."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the dependencies."""
        statuses = self._parameter("latest_version_status")
        installed_dependencies: List[Dict[str, str]] = []
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
            if dependency.get("latest-status", "unknown") in statuses
        ]
        return SourceMeasurement(total=str(len(installed_dependencies)), entities=entities)
