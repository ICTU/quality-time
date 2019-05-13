"""Gitlab metric source."""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from urllib.parse import quote

from dateutil.parser import parse
import requests

from ..collector import Collector
from ..type import Job, Jobs, Entities, URL, Value


class GitlabBase(Collector):
    """Baseclass for Gitlab collectors."""

    def gitlab_api_url(self, api: str, **parameters) -> URL:
        """Return a Gitlab API url with private token, if present in the parameters."""
        url = super().api_url(**parameters)
        project = quote(str(parameters.get("project")), safe="")
        api_url = f"{url}/api/v4/projects/{project}/{api}"
        private_token = parameters.get("private_token")
        if private_token:
            api_url += f"?private_token={private_token}"
        return URL(api_url)


class GitlabFailedJobs(GitlabBase):
    """Collector class to get failed job counts from Gitlab."""

    def api_url(self, **parameters) -> URL:
        return self.gitlab_api_url("jobs")

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(len(self.failed_jobs(response)))

    @staticmethod
    def basic_auth_credentials(**parameters) -> Optional[Tuple[str, str]]:
        return None  # The private token is passed as URI parameter

    def parse_source_response_entities(self, response: requests.Response, **parameters) -> Entities:
        return [
            dict(
                key=job["id"], name=job["ref"], url=job["web_url"], build_status=job["status"],
                build_age=str(self.build_age(job).days), build_date=str(self.build_datetime(job).date()))
            for job in self.failed_jobs(response)]

    def build_age(self, job: Job) -> timedelta:
        """Return the age of the job in days."""
        return datetime.now(timezone.utc) - self.build_datetime(job)

    @staticmethod
    def build_datetime(job: Job) -> datetime:
        """Return the build date of the job."""
        return parse(job["created_at"])

    @staticmethod
    def failed_jobs(response: requests.Response) -> Jobs:
        """Return the failed jobs."""
        return [job for job in response.json() if job["status"] == "failed"]


class GitlabSourceUpToDateness(GitlabBase):
    """Collector class to measure the up-to-dateness of a repo or folder/file in a repo."""

    def api_url(self, **parameters) -> URL:
        file_path = quote(parameters.get("file_path", ""), safe="")
        branch = quote(parameters.get("branch", "master"), safe="")
        return self.gitlab_api_url(f"repository/files/{file_path}?ref={branch}", **parameters)

    def landing_url(self, response: Optional[requests.Response], **parameters) -> URL:
        landing_url = super().landing_url(response, **parameters)
        project = parameters.get("project", "").strip("/")
        file_path = parameters.get("file_path", "").strip("/")
        branch = parameters.get("branch", "master").strip("/")
        return URL(f"{landing_url}/{project}/blob/{branch}/{file_path}")

    def get_source_response(self, api_url: URL, **parameters) -> requests.Response:
        """Override because we want to do a head request and get the last commit metadata."""
        response = requests.head(api_url, timeout=self.TIMEOUT)
        last_commit_id = response.headers["X-Gitlab-Last-Commit-Id"]
        commit_api_url = self.gitlab_api_url(f"repository/commits/{last_commit_id}", **parameters)
        return requests.get(commit_api_url, timeout=self.TIMEOUT)

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str((datetime.now(timezone.utc) - parse(response.json()["committed_date"])).days)
