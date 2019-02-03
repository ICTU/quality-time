"""Gitlab metric source."""

import requests

from collector.collector import Collector
from collector.type import Measurement, URL


class Gitlab(Collector):
    """Base class for Gitlab metrics."""
    name = "GitLab"


class GitlabVersion(Gitlab):
    """Return the Gitlab version."""

    def api_url(self, source) -> URL:
        return URL(f"{source.get('url')}/api/v4/version?private_token={source.get('private_token')}")

    def parse_source_response(self, response: requests.Response) -> Measurement:
        return Measurement(response.json()["version"])


class GitlabJobs(Gitlab):
    """Collector class to get job counts from Gitlab."""

    def api_url(self, source) -> URL:
        return URL(f"{source.get('url')}/api/v4/projects/{source.get('project')}/"
                   f"jobs?private_token={source.get('private_token')}")

    def parse_source_response(self, response: requests.Response) -> Measurement:
        return Measurement(len(response.json()))


class GitlabFailedJobs(GitlabJobs):
    """Collector class to get failed job counts from Gitlab."""

    def parse_source_response(self, response: requests.Response) -> Measurement:
        return Measurement(len([job for job in response.json() if job["status"] == "failed"]))
