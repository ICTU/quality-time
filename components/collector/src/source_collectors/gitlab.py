"""GitLab metric source."""

from abc import ABC
from datetime import datetime
from typing import cast, Iterator, List, Optional, Set, Tuple
from urllib.parse import quote

from dateutil.parser import parse
import requests

from collector_utilities.functions import days_ago
from collector_utilities.type import Job, Entities, Response, Responses, URL, Value
from .source_collector import SourceCollector, UnmergedBranchesSourceCollector


class GitLabBase(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for GitLab collectors."""

    def _gitlab_api_url(self, api: str) -> URL:
        """Return a GitLab API url with private token, if present in the parameters."""
        url = super()._api_url()
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

    def _api_url(self) -> URL:
        return self._gitlab_api_url("jobs")

    def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        entities = [
            dict(
                key=job["id"], name=job["name"], url=job["web_url"], build_status=job["status"], branch=job["ref"],
                stage=job["stage"], build_date=str((build_date := parse(job["created_at"])).date()),
                build_age=str(days_ago(build_date)))
            for job in self.__jobs(responses)]
        return str(len(entities)), "100", entities

    def __jobs(self, responses: Responses) -> Iterator[Job]:
        """Return the jobs to count."""
        jobs_seen: Set[Tuple[str, str, str]] = set()
        for response in responses:
            for job in response.json():
                job_fingerprint = job["name"], job["stage"], job["ref"]
                if job_fingerprint in jobs_seen:
                    continue
                jobs_seen.add(job_fingerprint)
                if self._count_job(job):
                    yield job

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

    def _api_url(self) -> URL:
        return self._gitlab_api_url("")

    def _landing_url(self, responses: Responses) -> URL:
        return URL(
            f"{responses[0].json()['web_url']}/blob/{self._parameter('branch', quote=True)}/"
            f"{self._parameter('file_path', quote=True)}") if responses else super()._landing_url(responses)

    def _get_source_responses(self, api_url: URL) -> Responses:
        """Override to get the last commit metadata of the file or, if the file is a folder, of the files in the folder,
        recursively."""

        def get_commits_recursively(file_path: str, first_call: bool = True) -> Responses:
            """Get the commits of files recursively."""
            tree_api = self._gitlab_api_url(
                f"repository/tree?path={file_path}&ref={self._parameter('branch', quote=True)}")
            tree_response = super(GitLabSourceUpToDateness, self)._get_source_responses(tree_api)[0]
            tree_response.raise_for_status()
            tree = tree_response.json()
            file_paths = [quote(item["path"], safe="") for item in tree if item["type"] == "blob"]
            folder_paths = [quote(item["path"], safe="") for item in tree if item["type"] == "tree"]
            if not tree and first_call:
                file_paths = [file_path]
            commit_responses = [self.__last_commit(file_path) for file_path in file_paths]
            for folder_path in folder_paths:
                commit_responses.extend(get_commits_recursively(folder_path, first_call=False))
            return commit_responses

        # First, get the project info so we can use the web url as landing url
        responses = super()._get_source_responses(api_url)
        responses[0].raise_for_status()
        # Then, collect the commits
        responses.extend(get_commits_recursively(str(self._parameter("file_path", quote=True))))
        return responses

    def __last_commit(self, file_path: str) -> Response:
        files_api_url = self._gitlab_api_url(
            f"repository/files/{file_path}?ref={self._parameter('branch', quote=True)}")
        response = requests.head(files_api_url)
        last_commit_id = response.headers["X-Gitlab-Last-Commit-Id"]
        commit_api_url = self._gitlab_api_url(f"repository/commits/{last_commit_id}")
        return requests.get(commit_api_url, timeout=self.TIMEOUT, auth=self._basic_auth_credentials())

    def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        commit_responses = responses[1:]
        value = str(days_ago(max(parse(response.json()["committed_date"]) for response in commit_responses)))
        return value, "100", []


class GitLabUnmergedBranches(GitLabBase, UnmergedBranchesSourceCollector):
    """Collector class to measure the number of unmerged branches."""

    def _api_url(self) -> URL:
        return self._gitlab_api_url("repository/branches")

    def _landing_url(self, responses: Responses) -> URL:
        return URL(f"{str(super()._landing_url(responses))}/{self._parameter('project')}/-/branches")

    def _unmerged_branches(self, responses: Responses) -> List:
        return [branch for branch in responses[0].json() if not branch["default"] and not branch["merged"] and
                days_ago(self._commit_datetime(branch)) > int(cast(str, self._parameter("inactive_days")))]

    def _commit_datetime(self, branch) -> datetime:
        return parse(branch["commit"]["committed_date"])
