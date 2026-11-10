"""Dependency-Track base collector."""

import asyncio
import json
from collections import defaultdict
from itertools import batched
from math import ceil
from operator import itemgetter
from typing import TYPE_CHECKING, Any, Literal

import ijson  # type: ignore[import-untyped]  # ijson has no type information

from base_collectors import TokenAuthenticationSourceCollector
from collector_utilities.exceptions import CollectorError
from collector_utilities.functions import add_query
from collector_utilities.type import URL, Response
from model import Entity, SourceResponses

from .json_types import DependencyTrackComponent

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Awaitable, Callable, Iterable

    from .json_types import DependencyTrackProject


class DependencyTrackComponentGraph:
    """The dependency graph of the components of one Dependency-Track project."""

    def __init__(self) -> None:
        self.__names: dict[str, str] = {}
        self.__parents: dict[str, set[str]] = defaultdict(set)

    def add_components(self, components: Iterable[DependencyTrackComponent]) -> None:
        """Add the components to the graph.

        Components can be added page by page. The graph only keeps the names of the components and their parent-child
        relations, so the components themselves need not be kept in memory.
        """
        for component in components:
            self.__names[component["uuid"]] = component["name"]
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

    PAGE_SIZE = 5000
    # Maximum number of pages to retrieve at the same time, so that big projects don't overload Dependency-Track.
    # Note that PAGE_SIZE * MAX_CONCURRENT_PAGES items can be in flight at the same time.
    MAX_CONCURRENT_PAGES = 5
    AUTH_HEADER = "X-Api-Key"

    async def _api_url(self) -> URL:
        """Override to add the API version."""
        return await super()._api_url() / "api/v1"

    def _landing_url_of_component(self, uuid: str) -> URL:
        """Return the landing URL of the component with the specified UUID."""
        return self.__landing_url() / f"components/{uuid}"

    def _landing_url_of_project(self, uuid: str) -> URL:
        """Return the landing URL of the project with the specified UUID."""
        return self.__landing_url() / f"projects/{uuid}"

    def __landing_url(self) -> URL:
        """Return the landing URL of the Dependency-Track instance."""
        return URL(str(self._parameter("landing_url")))

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to load multiple pages, if necessary."""
        responses = SourceResponses()
        for url in urls:
            async for pages in self.__get_page_batches(url, self.__read_response):
                responses.extend(SourceResponses(responses=pages))
        return responses

    async def _get_components(self, project_uuid: str) -> AsyncIterator[list[DependencyTrackComponent]]:
        """Yield the components of the project, page by page, in page order.

        Each component as returned by Dependency-Track contains the project, including the project's direct
        dependencies, so the size of a page is quadratic in the number of direct dependencies of the project. To
        not need memory for that, parse the components one by one while reading the response, and keep only the
        attributes the collector needs.
        """
        components_api = await self._api_url() / f"component/project/{project_uuid}"
        async for pages in self.__get_page_batches(components_api, self.__read_components):
            for page in pages:
                yield page

    async def __get_page_batches[T](
        self, url: URL, read_page: Callable[[Response], Awaitable[T]]
    ) -> AsyncIterator[list[T]]:
        """Yield all pages of the paginated URL, read with the read page function, in batches, in page order.

        The first page has to be retrieved first, because its X-Total-Count header tells how many pages there are.
        The other pages are retrieved in batches of at most MAX_CONCURRENT_PAGES, because retrieving them one by one
        would need one round trip per PAGE_SIZE items, which times out for projects with many components. Batching
        also bounds the number of requests that are prepared at the same time, no matter how big the total count is.
        """
        first_response = await self.__get_page(url, 1)  # Page numbers start at 1
        page_count = ceil(int(first_response.headers.get("X-Total-Count", 0)) / self.PAGE_SIZE)
        yield [await read_page(first_response)]
        del first_response  # Free memory
        for batch in batched(range(2, page_count + 1), self.MAX_CONCURRENT_PAGES, strict=False):
            yield await asyncio.gather(*[self.__get_and_read_page(url, page_nr, read_page) for page_nr in batch])

    async def __get_and_read_page[T](self, url: URL, page_nr: int, read_page: Callable[[Response], Awaitable[T]]) -> T:
        """Return one page of the paginated URL, read with the read page function."""
        return await read_page(await self.__get_page(url, page_nr))

    async def __get_page(self, url: URL, page_nr: int) -> Response:
        """Return the response for one page of the paginated URL, without reading it."""
        paginated_url = add_query(url, f"pageSize={self.PAGE_SIZE}&pageNumber={page_nr}")
        response: Response = (await super()._get_source_responses(paginated_url))[0]
        return response

    @staticmethod
    async def __read_response(response: Response) -> Response:
        """Read the response and return it."""
        # Retrieving consecutive big responses without reading the response hangs the client, see
        # https://github.com/aio-libs/aiohttp/issues/2217
        await response.read()
        return response

    @classmethod
    async def __read_components(cls, response: Response) -> list[DependencyTrackComponent]:
        """Read the components from the response, one by one, keeping only the attributes the collector needs."""
        return [cls.__slim_component(component) async for component in ijson.items_async(response.content, "item")]

    @staticmethod
    def __slim_component(component: dict[str, Any]) -> DependencyTrackComponent:
        """Return a copy of the component with only the attributes the collector needs."""
        slim_component = DependencyTrackComponent(name=component["name"], uuid=component["uuid"])
        if "directDependencies" in component:
            slim_component["directDependencies"] = component["directDependencies"]
        if "repositoryMeta" in component:
            slim_component["repositoryMeta"] = component["repositoryMeta"]
        if "version" in component:
            slim_component["version"] = component["version"]
        return slim_component

    async def _get_projects_by_uuid(self) -> dict[str, DependencyTrackProject]:
        """Return a mapping of project UUIDs to projects."""
        if projects := {project["uuid"]: project async for project in self._get_projects()}:
            return projects
        error_message = "No projects found"
        raise CollectorError(error_message)

    async def _get_projects(self) -> AsyncIterator[DependencyTrackProject]:
        """Return the Dependency-Track projects."""
        projects_api = await DependencyTrackBase._api_url(self) / "project"
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
