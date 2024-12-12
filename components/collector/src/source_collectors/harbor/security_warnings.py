"""Harbor security warnings collector."""

from abc import ABC
from typing import TypedDict, cast
from urllib.parse import quote, unquote

from base_collectors import SecurityWarningsSourceCollector, SourceCollector
from collector_utilities.exceptions import CollectorError
from collector_utilities.functions import match_string_or_regular_expression
from collector_utilities.type import URL
from model import Entities, Entity, SourceResponses


class HarborBase(SourceCollector, ABC):
    """Base class for Harbor collectors."""

    async def _api_url(self) -> URL:
        """Extend to add the Harbor REST API base path."""
        return URL(await super()._api_url() + "/api/v2.0")

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to follow Harbor pagination links, if necessary."""
        await self._check_credentials()
        all_responses = responses = await super()._get_source_responses(*urls)
        while next_urls := self._next_urls(responses):
            # Retrieving consecutive big responses without reading the response hangs the client, see
            # https://github.com/aio-libs/aiohttp/issues/2217
            for response in responses:
                await response.read()
            all_responses.extend(responses := await super()._get_source_responses(*next_urls))
        return all_responses

    async def _check_credentials(self) -> None:
        """Check that the credentials are valid.

        This needs to be done explicitly because Harbor doesn't throw an error on invalid credentials but quietly only
        returns public projects, making it hard for the user to see that there is something wrong.
        """
        if self._parameter("username"):
            # This will raise an exception for status >= 400:
            await super()._get_source_responses(URL(await self._api_url() + "/users/current"))

    def _next_urls(self, responses: SourceResponses) -> list[URL]:
        """Return the next (pagination) links from the responses."""
        return [URL(next_url) for response in responses if (next_url := response.links.get("next", {}).get("url"))]


class HarborScannerVulnerabilityReportError(CollectorError):
    """Harbor scanner vulnerability report error."""

    def __init__(self) -> None:
        super().__init__("Harbor scanner vulnerability report contains no known format")


class ScanOverview(TypedDict):
    """Type for the scan overview dict in the Harbor response."""

    scan_status: str
    summary: dict[str, int]


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
                if self._skip_project(project["name"]):
                    continue
                repositories_api = URL(f"{projects_api}/{project['name']}/repositories")
                responses.extend(await self._get_source_responses_for_project(project, repositories_api))
        return responses

    def _skip_project(self, project_name: str) -> bool:
        """Return whether the project should be skipped."""
        projects_to_ignore = self._parameter("projects_to_ignore")
        if projects_to_ignore and match_string_or_regular_expression(project_name, projects_to_ignore):
            return True
        projects_to_include = self._parameter("projects_to_include")
        return bool(projects_to_include and not match_string_or_regular_expression(project_name, projects_to_include))

    async def _get_source_responses_for_project(self, project, repositories_api: URL) -> SourceResponses:
        """Return the source responses for a specific project."""
        responses = SourceResponses()
        repositories_responses = await super()._get_source_responses(repositories_api)
        for repositories_response in repositories_responses:
            for repository in await repositories_response.json():
                repository_name = repository["name"].removeprefix(f"{project['name']}/")
                if self._skip_repository(repository_name):
                    continue
                # The repository name contains a slash. For some reason it needs to be encoded twice.
                repository_name = quote(quote(repository_name, safe=""), safe="")
                artifacts_api = URL(f"{repositories_api}/{repository_name}/artifacts?with_scan_overview=true")
                responses.extend(await super()._get_source_responses(artifacts_api))
        return responses

    def _skip_repository(self, repository_name: str) -> bool:
        """Return whether the repository should be skipped."""
        repositories_to_ignore = self._parameter("repositories_to_ignore")
        if repositories_to_ignore and match_string_or_regular_expression(repository_name, repositories_to_ignore):
            return True
        repositories_to_include = self._parameter("repositories_to_include")
        return bool(
            repositories_to_include and not match_string_or_regular_expression(repository_name, repositories_to_include)
        )

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the Harbor security warnings."""
        entities = Entities()
        for response in responses:
            json = await response.json(content_type=None)
            artifacts = [artifact for artifact in json if self._has_scan_with_warnings(artifact)]
            entities.extend([await self._create_entity(artifact) for artifact in artifacts])
        return entities

    async def _create_entity(self, artifact: dict) -> Entity:
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
            total=scan_summary.get("total", 0),
            fixable=scan_summary.get("fixable", 0),
        )

    def _has_scan_with_warnings(self, artifact) -> bool:
        """Return whether the artifact has a scan and the scan has security warnings."""
        if "scan_overview" in artifact:
            scan_overview = self._scan_overview(artifact)
            if scan_overview.get("scan_status", "").lower() == "success":
                scan_summary = scan_overview["summary"]
                return bool(scan_summary.get("total", 0) > 0)
        return False

    @staticmethod
    def _scan_overview(artifact) -> ScanOverview:
        """Return the scan overview or raise an exception."""
        vulnerability_report_keys = (
            "application/vnd.scanner.adapter.vuln.report.harbor+json; version=1.0",
            "application/vnd.security.vulnerability.report; version=1.1",
        )
        for key in vulnerability_report_keys:
            if key in artifact["scan_overview"]:
                return cast(ScanOverview, artifact["scan_overview"][key])
        raise HarborScannerVulnerabilityReportError
