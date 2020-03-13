"""GitLab metric source."""

import asyncio
import itertools
from abc import ABC
from datetime import datetime
from typing import cast, List, Optional, Set, Sequence, Tuple
from urllib.parse import quote

from dateutil.parser import parse

from collector_utilities.functions import days_ago, match_string_or_regular_expression
from collector_utilities.type import Job, Entities, Responses, URL, Value
from .source_collector import SourceCollector, UnmergedBranchesSourceCollector


class GitLabBase(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for GitLab collectors."""

    async def _gitlab_api_url(self, api: str) -> URL:
        """Return a GitLab API url with private token, if present in the parameters."""
        url = await super()._api_url()
        project = self._parameter("project", quote=True)
        api_url = f"{url}/api/v4/projects/{project}/{api}"
        sep = "&" if "?" in api_url else "?"
        api_url += f"{sep}per_page=100"
        if private_token := self._parameter("private_token"):
            api_url += f"&private_token={private_token}"
        return URL(api_url)

    def _basic_auth_credentials(self) -> Optional[Tuple[str, str]]:
        return None  # The private token is passed as URI parameter


class GitLabJobsBase(GitLabBase):
    """Base class for GitLab job collectors."""

    async def _api_url(self) -> URL:
        return await self._gitlab_api_url("jobs")

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        jobs = await self.__jobs(responses)
        entities = [
            dict(
                key=job["id"], name=job["name"], url=job["web_url"], build_status=job["status"], branch=job["ref"],
                stage=job["stage"], build_date=str((build_date := parse(job["created_at"])).date()),
                build_age=str(days_ago(build_date)))
            for job in jobs]
        return str(len(entities)), "100", entities

    async def __jobs(self, responses: Responses) -> Sequence[Job]:
        """Return the jobs to count."""
        jobs: List[Job] = []
        jobs_seen: Set[Tuple[str, str, str]] = set()
        for response in responses:
            for job in await response.json():
                job_fingerprint = job["name"], job["stage"], job["ref"]
                if job_fingerprint in jobs_seen:
                    continue
                jobs_seen.add(job_fingerprint)
                if self._count_job(job):
                    jobs.append(job)
        return jobs

    def _count_job(self, job: Job) -> bool:  # pylint: disable=no-self-use,unused-argument
        """Return whether to count the job."""
        raise NotImplementedError  # pragma: nocover


class GitLabFailedJobs(GitLabJobsBase):
    """Collector class to get failed job counts from GitLab."""

    def _count_job(self, job: Job) -> bool:
        """Return whether the job has failed."""
        failure_types = list(self._parameter("failure_type"))
        return job["status"] in failure_types


class GitLabUnusedJobs(GitLabJobsBase):
    """Collector class to get unused job counts from GitLab."""

    def _count_job(self, job: Job) -> bool:
        """Return whether the job is unused."""
        max_days = int(cast(str, self._parameter("inactive_job_days")))
        return days_ago(parse(job["created_at"])) > max_days


class GitLabSourceUpToDateness(GitLabBase):
    """Collector class to measure the up-to-dateness of a repo or folder/file in a repo."""

    async def _api_url(self) -> URL:
        return await self._gitlab_api_url("")

    async def _landing_url(self, responses: Responses) -> URL:
        if not responses:
            return await super()._landing_url(responses)
        web_url = (await responses[0].json())["web_url"]
        branch = self._parameter('branch', quote=True)
        file_path = self._parameter('file_path', quote=True)
        return URL(f"{web_url}/blob/{branch}/{file_path}")

    async def _get_source_responses(self, *urls: URL) -> Responses:
        """Override to get the last commit metadata of the file or, if the file is a folder, of the files in the folder,
        recursively."""

        async def get_commits_recursively(file_path: str, first_call: bool = True) -> Responses:
            """Get the commits of files recursively."""
            tree_api = await self._gitlab_api_url(
                f"repository/tree?path={file_path}&ref={self._parameter('branch', quote=True)}")
            tree_response = (await super(GitLabSourceUpToDateness, self)._get_source_responses(tree_api))[0]
            tree = await tree_response.json()
            file_paths = [quote(item["path"], safe="") for item in tree if item["type"] == "blob"]
            folder_paths = [quote(item["path"], safe="") for item in tree if item["type"] == "tree"]
            if not tree and first_call:
                file_paths = [file_path]
            commits = [self.__last_commit(file_path) for file_path in file_paths] + \
                [get_commits_recursively(folder_path, first_call=False) for folder_path in folder_paths]
            return list(itertools.chain(*(await asyncio.gather(*commits))))

        # First, get the project info so we can use the web url as landing url
        responses = await super()._get_source_responses(*urls)
        # Then, collect the commits
        responses.extend(await get_commits_recursively(str(self._parameter("file_path", quote=True))))
        return responses

    async def __last_commit(self, file_path: str) -> Responses:
        files_api_url = await self._gitlab_api_url(
            f"repository/files/{file_path}?ref={self._parameter('branch', quote=True)}")
        response = await self._session.head(files_api_url)
        last_commit_id = response.headers["X-Gitlab-Last-Commit-Id"]
        commit_api_url = await self._gitlab_api_url(f"repository/commits/{last_commit_id}")
        return await super()._get_source_responses(commit_api_url)

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        commit_responses = responses[1:]
        value = str(days_ago(max([parse((await response.json())["committed_date"]) for response in commit_responses])))
        return value, "100", []


class GitLabUnmergedBranches(GitLabBase, UnmergedBranchesSourceCollector):
    """Collector class to measure the number of unmerged branches."""

    async def _api_url(self) -> URL:
        return await self._gitlab_api_url("repository/branches")

    async def _landing_url(self, responses: Responses) -> URL:
        return URL(f"{str(await super()._landing_url(responses))}/{self._parameter('project')}/-/branches")

    async def _unmerged_branches(self, responses: Responses) -> List:
        branches = await responses[0].json()
        return [branch for branch in branches if not branch["default"] and not branch["merged"] and
                days_ago(self._commit_datetime(branch)) > int(cast(str, self._parameter("inactive_days"))) and
                not match_string_or_regular_expression(branch["name"], self._parameter("branches_to_ignore"))]

    def _commit_datetime(self, branch) -> datetime:
        return parse(branch["commit"]["committed_date"])
