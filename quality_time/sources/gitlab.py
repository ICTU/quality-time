"""Gitlab metric source."""

import requests

from quality_time.source import Source
from quality_time.type import Measurement, MeasurementResponse, URL


class GitlabVersion(Source):
    """Return the Gitlab version."""

    def api_url(self, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/api/v4/version?private_token={self.request.query.private_token}")

    def parse_source_response(self, metric: str, response: requests.Response) -> Measurement:
        return Measurement(response.json()["version"])


class GitlabJobs(Source):
    """Source class to get job counts from Gitlab."""

    def api_url(self, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/api/v4/projects/{self.request.query.project_id}/"
                   f"jobs?private_token={self.request.query.private_token}")

    def parse_source_response(self, metric: str, response: requests.Response) -> Measurement:
        return Measurement(len(response.json()))


class GitlabFailedJobs(Source):
    """Source class to get failed job counts from Gitlab."""

    def api_url(self, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/api/v4/projects/{self.request.query.project_id}/"
                   f"jobs?private_token={self.request.query.private_token}")

    def parse_source_response(self, metric: str, response: requests.Response) -> Measurement:
        return Measurement(len([job for job in response.json() if job["status"] == "failed"]))


class Gitlab(Source):
    """Gitlab source."""

    def get(self, metric: str) -> MeasurementResponse:
        delegate = dict(version=GitlabVersion, jobs=GitlabJobs, failed_jobs=GitlabFailedJobs)[metric]
        return delegate(self.request).get(metric)
