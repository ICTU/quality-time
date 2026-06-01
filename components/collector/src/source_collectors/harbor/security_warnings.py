"""Harbor security warnings collector."""

from abc import ABC
from typing import TypedDict, cast
from urllib.parse import quote, unquote

from base_collectors import LinkPaginationSourceCollector, SecurityWarningsSourceCollector
from collector_utilities.exceptions import CollectorError
from collector_utilities.type import URL
from model import Entities, Entity, SourceResponses

# Media types of the vulnerability report formats Harbor may use as keys in an artifact's scan overview:
VULNERABILITY_REPORT_KEYS = (
    "application/vnd.scanner.adapter.vuln.report.harbor+json; version=1.0",
    "application/vnd.security.vulnerability.report; version=1.1",
)


class HarborBase(LinkPaginationSourceCollector, ABC):
    """Base class for Harbor collectors."""

    async def _api_url(self) -> URL:
        """Extend to add the Harbor REST API base path."""
        return URL(await super()._api_url() + "/api/v2.0")

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to check the credentials before following the pagination links."""
        await self._check_credentials()
        return await super()._get_source_responses(*urls)

    async def _check_credentials(self) -> None:
        """Check that the user credentials are valid.

        Only works for real users. Robot users don't have a /current endpoint.

        This needs to be done explicitly because Harbor doesn't throw an error on invalid credentials but quietly only
        returns public projects, making it hard for the user to see that there is something wrong.
        """
        username = cast(str, self._parameter("username"))
        robot_account_prefix = cast(str, self._parameter("robot_account_prefix"))
        if username and not username.startswith(robot_account_prefix):
            # This will raise an exception for status >= 400:
            await super()._get_source_responses(URL(await self._api_url() + "/users/current"))


class HarborScannerVulnerabilityReportError(CollectorError):
    """Harbor scanner vulnerability report error."""

    def __init__(self) -> None:
        super().__init__("Harbor scanner vulnerability report contains no known format")


class Project(TypedDict):
    """Harbor project."""

    name: str


class ScanSummary(TypedDict):
    """Type for the scan summary in a scan overview in the Harbor response."""

    fixable: int
    total: int


class ScanOverview(TypedDict):
    """Type for the scan overview in the Harbor response."""

    key: str
    scan_status: str  # The status of the report generating process
    severity: str  # The overall severity
    summary: ScanSummary


class ArtifactTag(TypedDict):
    """Artifact tag."""

    name: str


class Artifact(TypedDict):
    """Harbor artifact type."""

    addition_links: dict[str, dict[str, str]]
    digest: str
    project_id: str
    scan_overview: dict[str, ScanOverview]
    tags: list[ArtifactTag]


class HarborSecurityWarnings(HarborBase, SecurityWarningsSourceCollector):
    """Harbor collector for security warnings."""

    ENTITY_SEVERITY_ATTRIBUTE = "highest_severity"
    MAKE_ENTITY_SEVERITY_VALUE_LOWER_CASE = True
    ENTITY_FIX_AVAILABILITY_ATTRIBUTE = "fixable"

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend because we need to do multiple requests to get all the data we need."""
        responses = SourceResponses()
        projects_api = URL(f"{await self._api_url()}/projects")
        projects_responses = await super()._get_source_responses(projects_api)
        for projects_response in projects_responses:
            for project in await projects_response.json():
                if self._include_project(project["name"]):
                    repositories_api = URL(f"{projects_api}/{project['name']}/repositories")
                    responses.extend(await self._get_source_responses_for_project(project, repositories_api))
        return responses

    def _include_project(self, project_name: str) -> bool:
        """Return whether the project should be include."""
        return self._matches_filter(project_name, "projects_to_include", "projects_to_ignore")

    async def _get_source_responses_for_project(self, project: Project, repositories_api: URL) -> SourceResponses:
        """Return the source responses for a specific project."""
        responses = SourceResponses()
        repositories_responses = await super()._get_source_responses(repositories_api)
        for repositories_response in repositories_responses:
            for repository in await repositories_response.json():
                repository_name = repository["name"].removeprefix(f"{project['name']}/")
                if self._include_repository(repository_name):
                    # The repository name contains a slash. For some reason it needs to be encoded twice.
                    repository_name = quote(quote(repository_name, safe=""), safe="")
                    artifacts_api = URL(f"{repositories_api}/{repository_name}/artifacts?with_scan_overview=true")
                    responses.extend(await super()._get_source_responses(artifacts_api))
        return responses

    def _include_repository(self, repository_name: str) -> bool:
        """Return whether the repository should be included."""
        return self._matches_filter(repository_name, "repositories_to_include", "repositories_to_ignore")

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the Harbor security warnings."""
        entities = Entities()
        for response in responses:
            json = await response.json(content_type=None)
            artifacts = [artifact for artifact in json if self._has_scan_with_warnings(artifact)]
            entities.extend([await self._create_entity(artifact) for artifact in artifacts])
        return entities

    async def _create_entity(self, artifact: Artifact) -> Entity:
        """Create an entity from the artifact."""
        scan_overview = self._scan_overview(artifact)
        scan_summary = scan_overview["summary"]
        digest = artifact["digest"].replace(" ", "")
        url = artifact["addition_links"]["vulnerabilities"]["href"]
        project = url.split("/projects/")[1].split("/repositories")[0]
        repository = unquote(url.split("/repositories/")[1].split("/artifacts/")[0])
        api_url = await super(HarborBase, self)._api_url()  # Get the base API URL without /api/v2.0
        project_id = artifact["project_id"]
        artifact_landing_url = (
            f"{api_url}/harbor/projects/{project_id}/repositories/{repository}/artifacts-tab/artifacts/{digest}"
        )
        return Entity(
            key=digest,
            url=artifact_landing_url,
            project=project,
            repository=unquote(repository),
            artifact=digest[:16],
            highest_severity=scan_overview.get("severity", "Unknown"),
            tags=", ".join(sorted(tag["name"] for tag in (artifact.get("tags") or []))),
            total=str(scan_summary.get("total", 0)),
            fixable=str(scan_summary.get("fixable", 0)),
        )

    @classmethod
    def _has_scan_with_warnings(cls, artifact: Artifact) -> bool:
        """Return whether the artifact has a scan and the scan has security warnings."""
        if "scan_overview" in artifact:
            scan_overview = cls._scan_overview(artifact)
            if scan_overview.get("scan_status", "").lower() == "success":
                scan_summary = scan_overview["summary"]
                return bool(scan_summary.get("total", 0) > 0)
        return False

    @staticmethod
    def _scan_overview(artifact: Artifact) -> ScanOverview:
        """Return the scan overview, or raise an exception if it has no known vulnerability report format."""
        scan_overview = artifact["scan_overview"]
        for key in VULNERABILITY_REPORT_KEYS:
            if key in scan_overview:
                return scan_overview[key]
        raise HarborScannerVulnerabilityReportError
