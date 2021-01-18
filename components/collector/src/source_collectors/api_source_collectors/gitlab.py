"""GitLab metric source."""

import asyncio
import itertools
from abc import ABC
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, cast
from urllib.parse import quote

from dateutil.parser import parse

from base_collectors import SourceCollector, UnmergedBranchesSourceCollector
from collector_utilities.functions import days_ago, match_string_or_regular_expression
from collector_utilities.type import URL, Job
from source_model import Entity, SourceMeasurement, SourceResponses


class GitLabBase(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for GitLab collectors."""

    async def _gitlab_api_url(self, api: str) -> URL:
        """Return a GitLab API url with private token, if present in the parameters."""
        url = await super()._api_url()
        project = self._parameter("project", quote=True)
        api_url = f"{url}/api/v4/projects/{project}" + (f"/{api}" if api else "")
        sep = "&" if "?" in api_url else "?"
        api_url += f"{sep}per_page=100"
        return URL(api_url)

    def _basic_auth_credentials(self) -> Optional[Tuple[str, str]]:
        return None  # The private token is passed as header

    def _headers(self) -> Dict[str, str]:
        headers = super()._headers()
        if private_token := self._parameter("private_token"):
            headers["Private-Token"] = str(private_token)
        return headers


class GitLabJobsBase(GitLabBase):
    """Base class for GitLab job collectors."""

    async def _api_url(self) -> URL:
        """Override to return the jobs API."""
        return await self._gitlab_api_url("jobs")

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the jobs from the responses."""
        jobs = await self.__jobs(responses)
        entities = [
            Entity(
                key=job["id"],
                name=job["name"],
                url=job["web_url"],
                build_status=job["status"],
                branch=job["ref"],
                stage=job["stage"],
                build_date=str(parse(job["created_at"]).date()),
            )
            for job in jobs
        ]
        return SourceMeasurement(entities=entities)

    async def __jobs(self, responses: SourceResponses) -> Sequence[Job]:
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

    def _count_job(self, job: Job) -> bool:
        """Return whether to count the job."""
        return not match_string_or_regular_expression(
            job["name"], self._parameter("jobs_to_ignore")
        ) and not match_string_or_regular_expression(job["ref"], self._parameter("refs_to_ignore"))


class GitLabFailedJobs(GitLabJobsBase):
    """Collector class to get failed job counts from GitLab."""

    async def _api_url(self) -> URL:
        """Extend to return only failed jobs."""
        return URL(str(await super()._api_url()) + "&scope=failed")

    def _count_job(self, job: Job) -> bool:
        """Return whether the job has failed."""
        failure_types = list(self._parameter("failure_type"))
        return super()._count_job(job) and job["status"] in failure_types


class GitLabUnusedJobs(GitLabJobsBase):
    """Collector class to get unused job counts from GitLab."""

    def _count_job(self, job: Job) -> bool:
        """Return whether the job is unused."""
        max_days = int(cast(str, self._parameter("inactive_job_days")))
        return super()._count_job(job) and days_ago(parse(job["created_at"])) > max_days


class GitLabSourceUpToDateness(GitLabBase):
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
            f"repository/tree?path={file_path}&ref={self._parameter('branch', quote=True)}"
        )
        tree_response = (await super()._get_source_responses(tree_api))[0]
        tree = await tree_response.json()
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
            f"repository/files/{file_path}?ref={self._parameter('branch', quote=True)}"
        )
        response = await self._session.head(files_api_url, headers=self._headers())
        last_commit_id = response.headers["X-Gitlab-Last-Commit-Id"]
        commit_api_url = await self._gitlab_api_url(f"repository/commits/{last_commit_id}")
        return await super()._get_source_responses(commit_api_url)

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the dates from the commits."""
        commit_responses = responses[1:]
        value = str(days_ago(max([parse((await response.json())["committed_date"]) for response in commit_responses])))
        return SourceMeasurement(value=value)


class GitLabUnmergedBranches(GitLabBase, UnmergedBranchesSourceCollector):
    """Collector class to measure the number of unmerged branches."""

    async def _api_url(self) -> URL:
        """Override to return the branches API."""
        return await self._gitlab_api_url("repository/branches")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the project branches."""
        return URL(f"{str(await super()._landing_url(responses))}/{self._parameter('project')}/-/branches")

    async def _unmerged_branches(self, responses: SourceResponses) -> List[Dict[str, Any]]:
        """Override to return a list of unmerged and inactive branches."""
        branches = await responses[0].json()
        return [
            branch
            for branch in branches
            if not branch["default"]
            and not branch["merged"]
            and days_ago(self._commit_datetime(branch)) > int(cast(str, self._parameter("inactive_days")))
            and not match_string_or_regular_expression(branch["name"], self._parameter("branches_to_ignore"))
        ]

    def _commit_datetime(self, branch) -> datetime:
        """Override to parse the commit date from the branch."""
        return parse(branch["commit"]["committed_date"])

    def _branch_landing_url(self, branch) -> URL:
        """Override to get the landing URL from the branch."""
        return URL(branch.get("web_url", ""))
