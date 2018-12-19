"""Gitlab metric source."""

import requests

from quality_time.source import Source
from quality_time.type import Measurement, URL


class Gitlab(Source):
    """Base class for Gitlab metrics."""
    name = "GitLab"


class GitlabVersion(Gitlab):
    """Return the Gitlab version."""

    def api_url(self, url: URL, component: str) -> URL:
        return URL(f"{url}/api/v4/version?private_token={self.query['private_token']}")

    def parse_source_response(self, response: requests.Response) -> Measurement:
        return Measurement(response.json()["version"])


class GitlabJobs(Gitlab):
    """Source class to get job counts from Gitlab."""

    def api_url(self, url: URL, component: str) -> URL:
        return URL(f"{url}/api/v4/projects/{self.query['project_id']}/"
                   f"jobs?private_token={self.query['private_token']}")

    def parse_source_response(self, response: requests.Response) -> Measurement:
        return Measurement(len(response.json()))


class GitlabFailedJobs(GitlabJobs):
    """Source class to get failed job counts from Gitlab."""

    def parse_source_response(self, response: requests.Response) -> Measurement:
        return Measurement(len([job for job in response.json() if job["status"] == "failed"]))
