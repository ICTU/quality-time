"""Dependency-Track base collector."""

from base_collectors import SourceCollector
from collector_utilities.type import URL
from model import SourceResponses


class DependencyTrackBase(SourceCollector):
    """Dependency-Track base class."""

    # Max page size is 100, see https://github.com/DependencyTrack/dependency-track/issues/209.
    # However, we use a lower number because pages may contain a lot of data, # especially for the
    # projects and findings endpoints.
    PAGE_SIZE = 25

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
            total_count = self.PAGE_SIZE + 1  # Total count is still unknown, make it so big we get at least one page
            while page_nr * self.PAGE_SIZE < total_count:
                offsetted_url = URL(f"{url}{"&" if "?" in url else "?"}pageSize={self.PAGE_SIZE}&pageNumber={page_nr}")
                response = (await super()._get_source_responses(offsetted_url))[0]
                total_count = int(response.headers.get("X-Total-Count", 0))
                responses.append(response)
                page_nr += 1
        return responses

    async def _get_project_uuids(self) -> dict[str, str]:
        """Return a mapping of project UUIDs to project names."""
        projects_api = URL(await self._api_url() + "/project")
        project_uuids = {}
        for response in await DependencyTrackBase._get_source_responses(self, projects_api):
            projects = await response.json(content_type=None)
            project_uuids.update({project["uuid"]: project["name"] for project in projects})
        return project_uuids
