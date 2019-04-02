"""Gitlab metric source."""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from urllib.parse import quote

from dateutil.parser import parse
import requests

from ..collector import Collector
from ..type import Job, Jobs, Units, URL, Value


class GitlabFailedJobs(Collector):
    """Collector class to get failed job counts from Gitlab."""

    def api_url(self, **parameters) -> URL:
        url = super().api_url(**parameters)
        project = quote(str(parameters.get("project")), safe="")
        api_url = f"{url}/api/v4/projects/{project}/jobs"
        private_token = parameters.get("private_token")
        if private_token:
            api_url += f"?private_token={private_token}"
        return URL(api_url)

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(len(self.failed_jobs(response)))

    @staticmethod
    def basic_auth_credentials(**parameters) -> Optional[Tuple[str, str]]:
        return None  # The private token is passed as URI parameter

    def parse_source_response_units(self, response: requests.Response, **parameters) -> Units:
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
