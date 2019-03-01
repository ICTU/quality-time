"""Gitlab metric source."""

import requests

from collector.collector import Collector
from collector.type import URL, Value


class GitlabJobs(Collector):
    """Collector class to get job counts from Gitlab."""

    def api_url(self, **parameters) -> URL:
        return URL(f"{parameters.get('url')}/api/v4/projects/{parameters.get('project')}/"
                   f"jobs?private_token={parameters.get('private_token')}")

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(len(response.json()))


class GitlabFailedJobs(GitlabJobs):
    """Collector class to get failed job counts from Gitlab."""

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(len([job for job in response.json() if job["status"] == "failed"]))
