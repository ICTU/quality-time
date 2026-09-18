"""Dependency-Track dependencies collector."""

from collections import defaultdict
from typing import TYPE_CHECKING

from collector_utilities.type import URL
from model import Entities, Entity, SourceResponses

from .base import DependencyTrackComponentGraph, DependencyTrackLatestVersionStatusBase

if TYPE_CHECKING:
    from .json_types import DependencyTrackComponent


class DependencyTrackDependencies(DependencyTrackLatestVersionStatusBase):
    """Dependency-Track collector for dependencies."""

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to get the components."""
        api_url = await self._api_url()
        project_uuids = await self._get_projects_by_uuid()
        project_components_urls = [URL(f"{api_url}/component/project/{uuid}") for uuid in project_uuids]
        return await super()._get_source_responses(*project_components_urls)

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Parse the entities from the responses."""
        components_by_project: dict[str, list[DependencyTrackComponent]] = defaultdict(list)
        for response in responses:
            for component in await response.json(content_type=None):
                components_by_project[component["project"]["uuid"]].append(component)
        entities = Entities()
        for components in components_by_project.values():
            # Create one dependency graph per project so the parent components can be looked up
            graph = DependencyTrackComponentGraph(components)
            entities.extend([self._create_entity(component, graph) for component in components])
        return entities

    def _create_entity(self, component: DependencyTrackComponent, graph: DependencyTrackComponentGraph) -> Entity:
        """Create an entity from the component."""
        project = component["project"]
        current_version = component.get("version", "unknown")
        latest_version = component.get("repositoryMeta", {}).get("latestVersion", "unknown")
        return Entity(
            component=component["name"],
            component_landing_url=self._landing_url_of_component(component["uuid"]),
            key=component["uuid"],
            latest=latest_version,
            latest_version_status=self._latest_version_status(current_version, latest_version),
            project=project["name"],
            project_landing_url=self._landing_url_of_project(project["uuid"]),
            project_version=project.get("version", ""),
            version=current_version,
            **self._parent_component_attributes(component["uuid"], graph),
        )
