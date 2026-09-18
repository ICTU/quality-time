"""Dependency-Track base collector."""

import asyncio
import json
from collections import defaultdict
from math import ceil
from operator import itemgetter
from typing import TYPE_CHECKING, Literal

from base_collectors import TokenAuthenticationSourceCollector
from collector_utilities.exceptions import CollectorError
from collector_utilities.functions import add_query
from collector_utilities.type import URL, Response
from model import Entity, SourceResponses

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from .json_types import DependencyTrackComponent, DependencyTrackProject


class DependencyTrackComponentGraph:
    """The dependency graph of the components of one Dependency-Track project."""

    def __init__(self, components: list[DependencyTrackComponent]) -> None:
        self.__names = {component["uuid"]: component["name"] for component in components}
        self.__parents: dict[str, set[str]] = defaultdict(set)
        for component in components:
            for child in json.loads(component.get("directDependencies") or "[]"):
                self.__parents[child["uuid"]].add(component["uuid"])

    def root_components(self, uuid: str) -> dict[str, str]:
        """Return the UUIDs and names of the project's direct dependencies that include the component, transitively.

        The result is empty if the project depends on the component directly, or if the component is unknown.
        """
        roots: set[str] = set()
        visited: set[str] = set()
        queue = [uuid]
        while queue:
            current = queue.pop()
            if current in visited:
                continue  # Guard against cycles in the graph
            visited.add(current)
            if parents := self.__parents.get(current):
                queue.extend(parents)
            elif current != uuid:  # A component without parents is a direct dependency of the project
                roots.add(current)
        named_roots = {root: self.__names[root] for root in roots}
        return dict(sorted(named_roots.items(), key=itemgetter(1, 0)))


class DependencyTrackBase(TokenAuthenticationSourceCollector):
    """Dependency-Track base class."""

    PAGE_SIZE = 1000
    # Maximum number of pages to retrieve at the same time, so that big projects don't overload Dependency-Track.
    # Note that PAGE_SIZE * MAX_CONCURRENT_PAGES items can be in flight at the same time.
    MAX_CONCURRENT_PAGES = 5
    AUTH_HEADER = "X-Api-Key"

    async def _api_url(self) -> URL:
        """Override to add the API version."""
        return URL((await super()._api_url()) + "/api/v1")

    def _landing_url_of_component(self, uuid: str) -> URL:
        """Return the landing URL of the component with the specified UUID."""
        return URL(f"{self.__landing_url()}/components/{uuid}")

    def _landing_url_of_project(self, uuid: str) -> URL:
        """Return the landing URL of the project with the specified UUID."""
        return URL(f"{self.__landing_url()}/projects/{uuid}")

    def __landing_url(self) -> str:
        """Return the landing URL of the Dependency-Track instance, without trailing slash."""
        return str(self._parameter("landing_url")).strip("/")

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to load multiple pages, if necessary."""
        responses = SourceResponses()
        for url in urls:
            for response in await self.__get_pages(url):
                responses.append(response)
        return responses

    async def __get_pages(self, url: URL) -> list[Response]:
        """Return all pages of the paginated URL, in page order.

        The first page has to be retrieved first, because its X-Total-Count header tells how many pages there are.
        The other pages are retrieved in batches of at most MAX_CONCURRENT_PAGES, because retrieving them one by one
        would need one round trip per PAGE_SIZE items, which times out for projects with many components. Batching
        also bounds the number of requests that are prepared at the same time, no matter how big the total count is.
        """
        pages = [await self.__get_page(url, 1)]  # Page numbers start at 1
        page_count = ceil(int(pages[0].headers.get("X-Total-Count", 0)) / self.PAGE_SIZE)
        for batch_start in range(2, page_count + 1, self.MAX_CONCURRENT_PAGES):
            batch = range(batch_start, min(batch_start + self.MAX_CONCURRENT_PAGES, page_count + 1))
            pages.extend(await asyncio.gather(*[self.__get_page(url, page_nr) for page_nr in batch]))
        return pages

    async def __get_page(self, url: URL, page_nr: int) -> Response:
        """Return one page of the paginated URL."""
        paginated_url = add_query(url, f"pageSize={self.PAGE_SIZE}&pageNumber={page_nr}")
        response: Response = (await super()._get_source_responses(paginated_url))[0]
        # Retrieving consecutive big responses without reading the response hangs the client, see
        # https://github.com/aio-libs/aiohttp/issues/2217
        await response.read()
        return response

    async def _get_projects_by_uuid(self) -> dict[str, DependencyTrackProject]:
        """Return a mapping of project UUIDs to projects."""
        if projects := {project["uuid"]: project async for project in self._get_projects()}:
            return projects
        error_message = "No projects found"
        raise CollectorError(error_message)

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
        for project in await response.json(content_type=None):
            if self._project_matches(project):
                yield project

    def _project_matches(self, project: DependencyTrackProject) -> bool:
        """Return whether the project name matches the project names and versions."""
        project_matches_name = self._matches_filter(project["name"], "project_names")
        project_matches_version = self._matches_filter(project.get("version", "unknown"), "project_versions")
        only_include_latest_project_version = self._parameter("only_include_latest_project_versions")
        project_matches_latest = not (only_include_latest_project_version == "yes" and not self._is_latest(project))
        return project_matches_name and project_matches_version and project_matches_latest

    @staticmethod
    def _latest_version_status(version: str, latest: str) -> Literal["unknown", "up-to-date", "update possible"]:
        """Return the latest version status."""
        if latest == "unknown":
            return "unknown"
        if latest == version:
            return "up-to-date"
        return "update possible"

    @staticmethod
    def _is_latest(project: DependencyTrackProject) -> bool:
        """Return whether the project is the latest version."""
        return project.get("isLatest", False)


class DependencyTrackLatestVersionStatusBase(DependencyTrackBase):
    """Base class for Dependency-Track collectors that can be filtered by latest version status."""

    def _root_component_attributes(self, uuid: str, graph: DependencyTrackComponentGraph) -> dict[str, str]:
        """Return the root component entity attributes for the component with the specified UUID."""
        roots = graph.root_components(uuid)
        attributes = {"root_component": ", ".join(roots.values())}
        if len(roots) == 1:  # Entity attributes support at most one URL, so only link if there's exactly one root
            attributes["root_component_landing_url"] = self._landing_url_of_component(next(iter(roots)))
        return attributes

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to include the entity in the measurement."""
        if not self._matches_filter(entity["component"], "components_to_include", "components_to_ignore"):
            return False
        has_latest_version_status = entity["latest_version_status"] in self._parameter("latest_version_status")
        return super()._include_entity(entity) and has_latest_version_status
