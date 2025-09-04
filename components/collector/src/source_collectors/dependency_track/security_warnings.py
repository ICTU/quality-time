"""Dependency-Track security warnings collector."""

from typing import TypedDict

from base_collectors import SecurityWarningsSourceCollector
from collector_utilities.type import URL
from model import Entities, Entity, SourceResponses

from .base import DependencyTrackLatestVersionStatusBase


class DependencyTrackComponent(TypedDict):
    """Component as returned by Dependency-Track."""

    latestVersion: str
    name: str
    project: str  # UUID of the project
    uuid: str
    version: str


class DependencyTrackVulnerability(TypedDict):
    """Vulnerability as returned by Dependency-Track."""

    vulnId: str
    description: str
    severity: str


class DependencyTrackFinding(TypedDict):
    """Finding as returned by Dependency-Track."""

    component: DependencyTrackComponent
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
        project_finding_urls = [URL(f"{api_url}/finding/project/{uuid}") for uuid in self._projects]
        return await super()._get_source_responses(*project_finding_urls)

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Parse the entities from the responses."""
        entities = Entities()
        for response in responses:
            findings = await response.json(content_type=None)
            entities.extend([self._create_entity(finding) for finding in findings])
        return entities

    def _create_entity(self, finding: DependencyTrackFinding) -> Entity:
        """Create an entity from the finding."""
        landing_url = str(self._parameter("landing_url")).strip("/")
        component = finding["component"]
        project_uuid = component["project"]
        vulnerability = finding["vulnerability"]
        current_version = component["version"]
        latest_version = component.get("latestVersion", "unknown")
        return Entity(
            component=component["name"],
            component_landing_url=f"{landing_url}/components/{component['uuid']}",
            description=vulnerability["description"],
            identifier=vulnerability["vulnId"],
            key=finding["matrix"],  # Matrix is a combination of project, component, and vulnerability
            latest=latest_version,
            latest_version_status=self._latest_version_status(current_version, latest_version),
            project=self._projects[project_uuid]["name"],
            project_landing_url=f"{landing_url}/projects/{project_uuid}",
            project_version=self._projects[project_uuid].get("version", ""),
            severity=vulnerability["severity"].capitalize(),
            version=current_version,
        )
