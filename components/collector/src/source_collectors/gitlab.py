"""Gitlab metric source."""

from datetime import datetime, timedelta, timezone
from typing import cast, List, Optional, Tuple
from urllib.parse import quote

from dateutil.parser import parse
import requests

from ..source_collector import SourceCollector
from ..type import Job, Jobs, Entities, URL, Value


class GitlabBase(SourceCollector):
    """Baseclass for Gitlab collectors."""

    def gitlab_api_url(self, api: str) -> URL:
        """Return a Gitlab API url with private token, if present in the parameters."""
        url = super().api_url()
        project = quote(str(self.parameters.get("project")), safe="")
        api_url = f"{url}/api/v4/projects/{project}/{api}"
        sep = "&" if "?" in api_url else "?"
        api_url += f"{sep}per_page=100"
        private_token = self.parameters.get("private_token")
        if private_token:
            api_url += f"&private_token={private_token}"
        return URL(api_url)

    def basic_auth_credentials(self) -> Optional[Tuple[str, str]]:
        return None  # The private token is passed as URI parameter


class GitlabFailedJobs(GitlabBase):
    """Collector class to get failed job counts from Gitlab."""

    def api_url(self) -> URL:
        return self.gitlab_api_url("jobs")

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        return str(len(self.failed_jobs(responses)))

    def parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        return [
            dict(
                key=job["id"], name=job["ref"], url=job["web_url"], build_status=job["status"],
                build_age=str(self.build_age(job).days), build_date=str(self.build_datetime(job).date()))
            for job in self.failed_jobs(responses)]

    def build_age(self, job: Job) -> timedelta:
        """Return the age of the job in days."""
        return datetime.now(timezone.utc) - self.build_datetime(job)

    @staticmethod
    def build_datetime(job: Job) -> datetime:
        """Return the build date of the job."""
        return parse(job["created_at"])

    @staticmethod
    def failed_jobs(responses: List[requests.Response]) -> Jobs:
        """Return the failed jobs."""
        return [job for response in responses for job in response.json() if job["status"] == "failed"]


class GitlabSourceUpToDateness(GitlabBase):
    """Collector class to measure the up-to-dateness of a repo or folder/file in a repo."""

    def api_url(self) -> URL:
        file_path = quote(cast(str, self.parameters.get("file_path", "")), safe="")
        branch = quote(cast(str, self.parameters.get("branch", "master")), safe="")
        return self.gitlab_api_url(f"repository/files/{file_path}?ref={branch}")

    def landing_url(self, responses: List[requests.Response]) -> URL:
        landing_url = super().landing_url(responses)
        project = cast(str, self.parameters.get("project", "")).strip("/")
        file_path = cast(str, self.parameters.get("file_path", "")).strip("/")
        branch = cast(str, self.parameters.get("branch", "master")).strip("/")
        return URL(f"{landing_url}/{project}/blob/{branch}/{file_path}")

    def get_source_responses(self, api_url: URL) -> List[requests.Response]:
        """Override because we want to do a head request and get the last commit metadata."""
        response = requests.head(api_url, timeout=self.TIMEOUT)
        last_commit_id = response.headers["X-Gitlab-Last-Commit-Id"]
        commit_api_url = self.gitlab_api_url(f"repository/commits/{last_commit_id}")
        return [requests.get(commit_api_url, timeout=self.TIMEOUT)]

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        return str((datetime.now(timezone.utc) - parse(responses[0].json()["committed_date"])).days)


class GitlabUnmergedBranches(GitlabBase):
    """Collector class to measure the number of unmerged branches."""

    def api_url(self) -> URL:
        return self.gitlab_api_url("repository/branches")

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        return str(len(self.unmerged_branches(responses)))

    def parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        return [
            dict(key=branch["name"], name=branch["name"], commit_age=str(self.commit_age(branch).days),
                 commit_date=str(self.commit_datetime(branch).date()))
            for branch in self.unmerged_branches(responses)]

    def unmerged_branches(self, responses: List[requests.Response]) -> List:
        """Return the unmerged branches."""
        return [branch for branch in responses[0].json() if branch["name"] != "master" and not branch["merged"] and
                self.commit_age(branch).days > int(cast(str, self.parameters.get("inactive_days") or "7"))]

    def commit_age(self, branch) -> timedelta:
        """Return the age of the last commit on the branch."""
        return datetime.now(timezone.utc) - self.commit_datetime(branch)

    @staticmethod
    def commit_datetime(branch) -> datetime:
        """Return the age of the last commit on the branch."""
        return parse(branch["commit"]["committed_date"])
