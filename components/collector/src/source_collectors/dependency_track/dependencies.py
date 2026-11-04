"""Dependency-Track dependencies collector."""

from typing import TYPE_CHECKING

from collector_utilities.type import URL
from model import Entities, Entity, SourceResponses

from .base import DependencyTrackComponentGraph, DependencyTrackLatestVersionStatusBase
from .json_types import DependencyTrackComponent

if TYPE_CHECKING:
    from .json_types import DependencyTrackProject


class DependencyTrackDependencies(DependencyTrackLatestVersionStatusBase):
    """Dependency-Track collector for dependencies."""

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to get the components and their dependency graph, per project.

        The components are processed page by page, keeping only the attributes needed to create the entities, so
        that the responses for projects with many components don't need to be kept in memory. As the components are
        kept by the collector, the source responses are empty.
        """
        api_url = await self._api_url()
        self._components: list[tuple[DependencyTrackComponentGraph, list[DependencyTrackComponent]]] = []
        for project_uuid, project in (await self._get_projects_by_uuid()).items():
            # Create one dependency graph per project so the root components can be looked up
            graph = DependencyTrackComponentGraph()
            components: list[DependencyTrackComponent] = []
            async for page in self._get_paginated_items(URL(f"{api_url}/component/project/{project_uuid}")):
                graph.add_components(page)
                components.extend(self._slim_component(component, project) for component in page)
            self._components.append((graph, components))
        return SourceResponses()

    @staticmethod
    def _slim_component(
        component: DependencyTrackComponent, project: DependencyTrackProject
    ) -> DependencyTrackComponent:
        """Return a copy of the component with only the attributes needed to create the entity.

        The copy refers to the project instead of having its own copy of the project, to save memory.
        """
        slim_component = DependencyTrackComponent(name=component["name"], project=project, uuid=component["uuid"])
        if "repositoryMeta" in component:
            slim_component["repositoryMeta"] = component["repositoryMeta"]
        if "version" in component:
            slim_component["version"] = component["version"]
        return slim_component

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Parse the entities from the components."""
        entities = Entities()
        for graph, components in self._components:
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
            **self._root_component_attributes(component["uuid"], graph),
        )
