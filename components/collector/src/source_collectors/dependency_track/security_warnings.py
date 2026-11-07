"""Dependency-Track security warnings collector."""

from typing import TYPE_CHECKING, NotRequired, TypedDict

from base_collectors import SecurityWarningsSourceCollector
from model import Entities, Entity, SourceResponses

from .base import DependencyTrackComponentGraph, DependencyTrackLatestVersionStatusBase

if TYPE_CHECKING:
    from collector_utilities.type import URL


class DependencyTrackFindingComponent(TypedDict):
    """Component as returned by the Dependency-Track finding API."""

    latestVersion: str
    name: str
    project: str  # UUID of the project
    uuid: str
    version: str


class DependencyTrackVulnerability(TypedDict):
    """Vulnerability as returned by Dependency-Track."""

    vulnId: str
    description: NotRequired[str]
    severity: NotRequired[str]


class DependencyTrackFinding(TypedDict):
    """Finding as returned by Dependency-Track."""

    component: DependencyTrackFindingComponent
    # Matrix is a combination of project, component, and vulnerability, see
    # https://github.com/DependencyTrack/dependency-track/blob/757a9664d67aaec510f2ec651da4f28b9d1ec16e/src/main/java/org/dependencytrack/model/Finding.java#L267
    matrix: str
    vulnerability: DependencyTrackVulnerability


class DependencyTrackSecurityWarnings(SecurityWarningsSourceCollector, DependencyTrackLatestVersionStatusBase):
    """Dependency-Track collector for security warnings."""

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to get the findings."""
        api_url = await self._api_url()
        self._projects = await self._get_projects_by_uuid()
        # The findings API returns no dependency graph information, so retrieve the components of each project to
        # be able to determine the root components of the vulnerable components
        self._graphs = {uuid: await self._get_component_graph(uuid) for uuid in self._projects}
        project_finding_urls = [api_url / f"finding/project/{uuid}" for uuid in self._projects]
        return await super()._get_source_responses(*project_finding_urls)

    async def _get_component_graph(self, project_uuid: str) -> DependencyTrackComponentGraph:
        """Return the dependency graph of the components of the project."""
        graph = DependencyTrackComponentGraph()
        # Add the components to the graph page by page, so that only the graph is kept in memory and not the
        # components. Don't add the responses to the source responses, so that only the findings are parsed into
        # entities.
        async for components in self._get_components(project_uuid):
            graph.add_components(components)
        return graph

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Parse the entities from the responses."""
        entities = Entities()
        for response in responses:
            findings = await response.json(content_type=None)
            entities.extend([self._create_entity(finding) for finding in findings])
        return entities

    def _create_entity(self, finding: DependencyTrackFinding) -> Entity:
        """Create an entity from the finding."""
        component = finding["component"]
        project_uuid = component["project"]
        vulnerability = finding["vulnerability"]
        current_version = component["version"]
        latest_version = component.get("latestVersion", "unknown")
        return Entity(
            component=component["name"],
            component_landing_url=self._landing_url_of_component(component["uuid"]),
            description=vulnerability.get("description", ""),
            identifier=vulnerability["vulnId"],
            key=finding["matrix"],  # Matrix is a combination of project, component, and vulnerability
            latest=latest_version,
            latest_version_status=self._latest_version_status(current_version, latest_version),
            project=self._projects[project_uuid]["name"],
            project_landing_url=self._landing_url_of_project(project_uuid),
            project_version=self._projects[project_uuid].get("version", ""),
            severity=vulnerability.get("severity", "UNASSIGNED").capitalize(),
            version=current_version,
            **self._root_component_attributes(component["uuid"], self._graphs[project_uuid]),
        )
