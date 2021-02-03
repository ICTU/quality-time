"""Azure Devops Server up-to-dateness collector."""

from abc import ABC
from datetime import datetime

import aiohttp
from dateutil.parser import parse

from base_collectors import SourceCollector, SourceUpToDatenessCollector
from collector_utilities.type import URL, Response
from source_model import SourceMeasurement, SourceResponses

from .base import AzureDevopsRepositoryBase
from .jobs import AzureDevopsJobs


class AzureDevopsFileUpToDateness(SourceUpToDatenessCollector, AzureDevopsRepositoryBase):
    """Collector class to measure the up-to-dateness of a repo or folder/file in a repo."""

    async def _api_url(self) -> URL:
        """Extend to add the commit API path and associated parameters."""
        api_url = str(await super()._api_url())
        repository_id = await self._repository_id()
        path = self._parameter("file_path", quote=True)
        branch = self._parameter("branch", quote=True)
        search_criteria = (
            f"searchCriteria.itemPath={path}&searchCriteria.itemVersion.version={branch}&searchCriteria.$top=1"
        )
        return URL(f"{api_url}/_apis/git/repositories/{repository_id}/commits?{search_criteria}&api-version=4.1")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add a path to the file."""
        landing_url = str(await super()._landing_url(responses))
        repository = self._parameter("repository") or landing_url.rsplit("/", 1)[-1]
        path = self._parameter("file_path", quote=True)
        branch = self._parameter("branch", quote=True)
        return URL(f"{landing_url}/_git/{repository}?path={path}&version=GB{branch}")

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to get the date and time of the commit or the pipeline."""
        json_value = (await response.json())["value"]
        return parse(json_value[0]["committer"]["date"])


class AzureDevopsJobUpToDateness(SourceUpToDatenessCollector, AzureDevopsJobs):
    """Collector class to measure the up-to-dateness of a job/pipeline."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to get the date and time of the commit or the pipeline."""
        json_value = (await response.json())["value"]
        build_date_times = [self._latest_build_date_time(job) for job in json_value if self._include_job(job)]
        return max(build_date_times, default=datetime.min)


class AzureDevopsSourceUpToDateness(SourceCollector, ABC):
    """Factory class to create a collector to get the up-to-dateness of either jobs or files."""

    def __new__(cls, session: aiohttp.ClientSession, source, data_model):
        """Create an instance of either the file up-to-dateness collector or the jobs up-to-dateness collector."""
        file_path = source.get("parameters", {}).get("file_path")
        collector_class = AzureDevopsFileUpToDateness if file_path else AzureDevopsJobUpToDateness
        instance = collector_class(session, source, data_model)
        instance.source_type = cls.source_type
        return instance

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to document that this class does not parse responses itself."""
        raise NotImplementedError
