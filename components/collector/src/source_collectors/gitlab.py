"""Gitlab metric source."""

from abc import ABC
from datetime import datetime, timedelta, timezone
from typing import cast, List, Optional, Tuple
from urllib.parse import quote

from dateutil.parser import parse
import requests

from collector_utilities.type import Job, Jobs, Entities, Responses, URL, Value
from .source_collector import SourceCollector, UnmergedBranchesSourceCollector


class GitlabBase(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Baseclass for Gitlab collectors."""

    def _gitlab_api_url(self, api: str) -> URL:
        """Return a Gitlab API url with private token, if present in the parameters."""
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


class GitlabFailedJobs(GitlabBase):
    """Collector class to get failed job counts from Gitlab."""

    def _api_url(self) -> URL:
        return self._gitlab_api_url("jobs")

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(len(self.__failed_jobs(responses)))

    def _parse_source_responses_entities(self, responses: Responses) -> Entities:
        return [
            dict(
                key=job["id"], name=job["ref"], url=job["web_url"], build_status=job["status"],
                build_age=str(self.__build_age(job).days), build_date=str(self.__build_datetime(job).date()))
            for job in self.__failed_jobs(responses)]

    def __build_age(self, job: Job) -> timedelta:
        """Return the age of the job in days."""
        return datetime.now(timezone.utc) - self.__build_datetime(job)

    @staticmethod
    def __build_datetime(job: Job) -> datetime:
        """Return the build date of the job."""
        return parse(job["created_at"])

    @staticmethod
    def __failed_jobs(responses: Responses) -> Jobs:
        """Return the failed jobs."""
        return [job for response in responses for job in response.json() if job["status"] == "failed"]


class GitlabSourceUpToDateness(GitlabBase):
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
            tree_response = super(GitlabSourceUpToDateness, self)._get_source_responses(tree_api)[0]
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

    def __last_commit(self, file_path: str) -> requests.Response:
        files_api_url = self._gitlab_api_url(
            f"repository/files/{file_path}?ref={self._parameter('branch', quote=True)}")
        response = requests.head(files_api_url)
        last_commit_id = response.headers["X-Gitlab-Last-Commit-Id"]
        commit_api_url = self._gitlab_api_url(f"repository/commits/{last_commit_id}")
        return requests.get(commit_api_url, timeout=self.TIMEOUT, auth=self._basic_auth_credentials())

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        commit_responses = responses[1:]
        return str(min((datetime.now(timezone.utc) - parse(response.json()["committed_date"])).days
                       for response in commit_responses))


class GitlabUnmergedBranches(GitlabBase, UnmergedBranchesSourceCollector):
    """Collector class to measure the number of unmerged branches."""

    def _api_url(self) -> URL:
        return self._gitlab_api_url("repository/branches")

    def _landing_url(self, responses: Responses) -> URL:
        return URL(f"{str(super()._landing_url(responses))}/{self._parameter('project')}/-/branches")

    def _unmerged_branches(self, responses: Responses) -> List:
        return [branch for branch in responses[0].json() if not branch["default"] and not branch["merged"] and
                self._commit_age(branch).days > int(cast(str, self._parameter("inactive_days")))]

    def _commit_datetime(self, branch) -> datetime:
        return parse(branch["commit"]["committed_date"])
