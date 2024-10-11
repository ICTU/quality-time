"""Dependency-Track base collector."""

from collections.abc import AsyncIterator
from typing import Literal, TypedDict, cast

from base_collectors import SourceCollector
from collector_utilities.functions import add_query, match_string_or_regular_expression
from collector_utilities.type import URL, Response
from model import Entity, SourceResponses


class DependencyTrackProject(TypedDict):
    """Project as returned by Dependency-Track."""

    # Last BOM import is a Unix timestamp, despite the Dependency-Tracker Swagger docs saying it's a datetime string
    # See https://github.com/DependencyTrack/dependency-track/issues/840
    lastBomImport: int
    name: str
    uuid: str
    version: str


class DependencyTrackBase(SourceCollector):
    """Dependency-Track base class."""

    # Max page size is 100, see https://github.com/DependencyTrack/dependency-track/issues/209.
    PAGE_SIZE = 100

    async def _api_url(self) -> URL:
        """Override to add the API version."""
        return URL((await super()._api_url()) + "/api/v1")

    def _headers(self) -> dict[str, str]:
        """Return the headers for the get request."""
        headers = super()._headers()
        if api_key := str(self._parameter("private_token")):
            headers["X-Api-Key"] = api_key
        return headers

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to load multiple pages, if necessary."""
        responses = SourceResponses()
        for url in urls:
            page_nr = 1  # Page numbers start at 1
            total_count = 1  # Total count is still unknown, make sure we retrieve at least one page
            while (page_nr - 1) * self.PAGE_SIZE < total_count:
                offsetted_url = add_query(url, f"pageSize={self.PAGE_SIZE}&pageNumber={page_nr}")
                response = (await super()._get_source_responses(offsetted_url))[0]
                # Retrieving consecutive big responses without reading the response hangs the client, see
                # https://github.com/aio-libs/aiohttp/issues/2217
                await response.read()
                total_count = int(response.headers.get("X-Total-Count", 0))
                responses.append(response)
                page_nr += 1
        return responses

    async def _get_project_uuids(self) -> dict[str, str]:
        """Return a mapping of project UUIDs to project names."""
        return {project["uuid"]: project["name"] async for project in self._get_projects()}

    async def _get_projects(self) -> AsyncIterator[DependencyTrackProject]:
        """Return the Dependency-Track projects."""
        projects_api = URL(await DependencyTrackBase._api_url(self) + "/project")
        for response in await DependencyTrackBase._get_source_responses(self, projects_api):
            # We need an async for-loop and yield projects one by one because Python has no `async yield from`,
            # see https://peps.python.org/pep-0525/#asynchronous-yield-from
            async for project in self._get_projects_from_response(response):
                yield project

    async def _get_projects_from_response(self, response: Response) -> AsyncIterator[DependencyTrackProject]:
        """Return the projects from the response that match the configured project names and versions."""
        project_names = cast(list, self._parameter("project_names"))
        project_versions = cast(list, self._parameter("project_versions"))
        for project in await response.json(content_type=None):
            if self._project_matches(project, project_names, project_versions):
                yield project

    @staticmethod
    def _project_matches(project: DependencyTrackProject, names: list[str], versions: list[str]) -> bool:
        """Return whether the project name matches the project names and versions."""
        project_matches_name = match_string_or_regular_expression(project["name"], names) if names else True
        project_matches_version = match_string_or_regular_expression(project["version"], versions) if versions else True
        return project_matches_name and project_matches_version

    @staticmethod
    def _latest_version_status(version: str, latest: str) -> Literal["unknown", "up-to-date", "update possible"]:
        """Return the latest version status."""
        if latest == "unknown":
            return "unknown"
        if latest == version:
            return "up-to-date"
        return "update possible"


class DependencyTrackLatestVersionStatusBase(DependencyTrackBase):
    """Base class for Dependency-Track collectors that can be filtered by latest version status."""

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to include the entity in the measurement."""
        has_latest_version_status = entity["latest_version_status"] in self._parameter("latest_version_status")
        return super()._include_entity(entity) and has_latest_version_status
