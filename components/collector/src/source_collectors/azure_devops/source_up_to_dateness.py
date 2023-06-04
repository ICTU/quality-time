"""Azure DevOps Server up-to-dateness collector."""

from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, cast

from base_collectors import SourceCollector, TimePassedCollector
from collector_utilities.date_time import MIN_DATETIME, parse_datetime
from collector_utilities.type import URL, Response
from model import SourceMeasurement, SourceResponses

from .base import AzureDevopsJobs, AzureDevopsRepositoryBase

if TYPE_CHECKING:
    from datetime import datetime

    import aiohttp


class AzureDevopsFileUpToDateness(TimePassedCollector, AzureDevopsRepositoryBase):
    """Collector class to measure the up-to-dateness of a repo or folder/file in a repo."""

    async def _api_url(self) -> URL:
        """Extend to add the commit API path and associated parameters."""
        api_url = str(await super()._api_url())
        path = self._parameter("file_path", quote=True)
        branch = self._parameter("branch", quote=True)
        search_criteria = (
            f"searchCriteria.itemPath={path}&searchCriteria.itemVersion.version={branch}&searchCriteria.$top=1"
        )
        return URL(f"{api_url}/commits?{search_criteria}&api-version=4.1")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add a path to the file."""
        landing_url = str(await super()._landing_url(responses))
        path = self._parameter("file_path", quote=True)
        branch = self._parameter("branch", quote=True)
        return URL(f"{landing_url}?path={path}&version=GB{branch}")

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to get the date and time of the commit or the pipeline."""
        json_value = (await response.json())["value"]
        return parse_datetime(json_value[0]["committer"]["date"])


class AzureDevopsJobUpToDateness(TimePassedCollector, AzureDevopsJobs):  # lgtm [py/conflicting-attributes]
    """Collector class to measure the up-to-dateness of a job/pipeline."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to get the date and time of the commit or the pipeline."""
        entities = await self._parse_entities(SourceResponses(responses=[response]))  # parse, to call _include_entity
        build_date_times = [parse_datetime(entity["build_date"]) for entity in entities if self._include_entity(entity)]
        return max(build_date_times, default=MIN_DATETIME)


class AzureDevopsSourceUpToDateness(SourceCollector, ABC):
    """Factory class to create a collector to get the up-to-dateness of either jobs or files."""

    def __new__(cls, session: aiohttp.ClientSession, source) -> AzureDevopsSourceUpToDateness:
        """Create an instance of either the file up-to-dateness collector or the jobs up-to-dateness collector."""
        file_path = source.get("parameters", {}).get("file_path")
        collector_class = AzureDevopsFileUpToDateness if file_path else AzureDevopsJobUpToDateness
        instance = collector_class(session, source)
        instance.source_type = cls.source_type
        return cast(AzureDevopsSourceUpToDateness, instance)

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to document that this class does not parse responses itself."""
        raise NotImplementedError
