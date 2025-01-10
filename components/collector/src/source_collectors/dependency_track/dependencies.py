"""Dependency-Track security warnings collector."""

from typing import TypedDict

from collector_utilities.type import URL
from model import Entities, Entity, SourceResponses

from .base import DependencyTrackLatestVersionStatusBase, DependencyTrackProject


class DependencyTrackRepositoryMetaData(TypedDict):
    """Repository meta data as returned by Dependency-Track."""

    latestVersion: str


class DependencyTrackComponent(TypedDict, total=False):
    """Component as returned by Dependency-Track."""

    name: str
    project: DependencyTrackProject
    repositoryMeta: DependencyTrackRepositoryMetaData
    uuid: str
    version: str


class DependencyTrackDependencies(DependencyTrackLatestVersionStatusBase):
    """Dependency-Track collector for security warnings."""

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to get the components."""
        api_url = await self._api_url()
        project_uuids = await self._get_project_uuids()
        project_components_urls = [URL(f"{api_url}/component/project/{uuid}") for uuid in project_uuids]
        return await super()._get_source_responses(*project_components_urls)

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Parse the entities from the responses."""
        entities = Entities()
        for response in responses:
            components = await response.json(content_type=None)
            entities.extend([self._create_entity(component) for component in components])
        return entities

    def _create_entity(self, component: DependencyTrackComponent) -> Entity:
        """Create an entity from the component."""
        project = component["project"]
        current_version = component["version"]
        latest_version = component.get("repositoryMeta", {}).get("latestVersion", "unknown")
        landing_url = str(self._parameter("landing_url")).strip("/")
        return Entity(
            component=component["name"],
            component_landing_url=f"{landing_url}/components/{component['uuid']}",
            key=component["uuid"],
            latest=latest_version,
            latest_version_status=self._latest_version_status(current_version, latest_version),
            project=project["name"],
            project_landing_url=f"{landing_url}/projects/{project['uuid']}",
            version=current_version,
        )
