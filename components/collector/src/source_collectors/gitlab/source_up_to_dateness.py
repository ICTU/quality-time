"""GitLab source up-to-dateness collector."""

import asyncio
import itertools
from abc import ABC
from http import HTTPStatus
from typing import TYPE_CHECKING, Self, cast
from urllib.parse import quote

import aiohttp

from base_collectors import SourceCollector, TimePassedCollector
from collector_utilities.date_time import days_ago, parse_datetime
from collector_utilities.exceptions import CollectorError
from collector_utilities.type import URL, Response, Value
from model import Entities, SourceMeasurement, SourceResponses

from .base import GitLabPipelineBase, GitLabProjectBase

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime


class GitLabFileUpToDateness(GitLabProjectBase):
    """Collector class to measure the up-to-dateness of a repo or folder/file in a repo."""

    async def _api_url(self) -> URL:
        """Override to return the API URL."""
        return await self._gitlab_api_url("")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Override to return a landing URL for the folder or file."""
        if not responses:
            return await super()._landing_url(responses)
        web_url = (await responses[0].json())["web_url"]
        branch = self._parameter("branch", quote=True)
        file_path = self._parameter("file_path", quote=True)
        return URL(f"{web_url}/blob/{branch}/{file_path}")

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Get the last commit metadata of the file or, in case of a folder, of the files in the folder, recursively."""
        # First, get the project info so we can use the web url as landing url
        responses = await super()._get_source_responses(*urls)
        # Then, collect the commits
        responses.extend(await self.__get_commits_recursively(str(self._parameter("file_path", quote=True))))
        return responses

    async def __get_commits_recursively(self, file_path: str, first_call: bool = True) -> SourceResponses:
        """Get the commits of files recursively."""
        tree_api = await self._gitlab_api_url(
            f"repository/tree?path={file_path}&ref={self._parameter('branch', quote=True)}",
        )
        try:
            tree_response = (await super()._get_source_responses(tree_api))[0]
            tree = await tree_response.json()
        except aiohttp.ClientResponseError as message:
            if first_call and message.status == HTTPStatus.NOT_FOUND:
                # The repository/tree endpoint always returns 404 for file paths since GitLab v17.7, so we ignore the
                # error. If the path is a file and does not exist, retrieving the last commit will fail and that
                # error will then tell the user they entered the path of a non-existing file.
                tree = []
            else:
                raise
        file_paths = [quote(item["path"], safe="") for item in tree if item["type"] == "blob"]
        folder_paths = [quote(item["path"], safe="") for item in tree if item["type"] == "tree"]
        if not tree and first_call:
            file_paths = [file_path]
        commits = [self.__last_commit(file_path) for file_path in file_paths] + [
            self.__get_commits_recursively(folder_path, first_call=False) for folder_path in folder_paths
        ]
        return SourceResponses(responses=list(itertools.chain(*(await asyncio.gather(*commits)))))

    async def __last_commit(self, file_path: str) -> SourceResponses:
        """Return the last, meaning the most recent, commit."""
        files_api_url = await self._gitlab_api_url(
            f"repository/files/{file_path}?ref={self._parameter('branch', quote=True)}",
        )
        response = await self._session.head(files_api_url, headers=self._headers())
        last_commit_id = response.headers["X-Gitlab-Last-Commit-Id"]
        commit_api_url = await self._gitlab_api_url(f"repository/commits/{last_commit_id}")
        return await super()._get_source_responses(commit_api_url)

    async def _parse_value(self, responses: SourceResponses, included_entities: Entities) -> Value:
        """Override to parse the dates from the commits."""
        commit_responses = responses[1:]
        commit_dates = [parse_datetime((await response.json())["committed_date"]) for response in commit_responses]
        return str(days_ago(max(commit_dates)))


class GitLabPipelineUpToDateness(TimePassedCollector, GitLabPipelineBase):
    """Collector class to measure the up-to-dateness of a pipeline."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to get the date and time of the pipeline."""
        pipelines = await self._pipelines(SourceResponses(responses=[response]))
        if datetimes := [pipeline.datetime for pipeline in pipelines]:
            return self.minimum(datetimes)
        error_message = "No pipelines found within the lookback period"
        raise CollectorError(error_message)

    def minimum(self, date_times: Sequence[datetime]) -> datetime:
        """Override to return the newest datetime."""
        return max(date_times)


class GitLabSourceUpToDateness(SourceCollector, ABC):
    """Factory class to create a collector to get the up-to-dateness of either pipelines or files."""

    def __new__(cls, session: aiohttp.ClientSession, metric, source) -> Self:
        """Create an instance of either the file up-to-dateness collector or the jobs up-to-dateness collector."""
        file_path = source.get("parameters", {}).get("file_path")
        collector_class = GitLabFileUpToDateness if file_path else GitLabPipelineUpToDateness
        instance = collector_class(session, metric, source)
        instance.source_type = cls.source_type
        return cast(Self, instance)

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to document that this class does not parse responses itself."""
        raise NotImplementedError
