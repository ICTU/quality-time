"""Gitlab metric source."""

import requests

from quality_time.source import Source
from quality_time.type import Measurement, MeasurementResponse, URL


class GitlabVersion(Source):
    """Return the Gitlab version."""

    def api_url(self, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/api/v4/version?private_token={self.request.query.private_token}")

    @classmethod
    def parse_source_response(cls, metric: str, response: requests.Response) -> Measurement:
        return Measurement(response.json()["version"])


class GitlabJobs(Source):
    """Source class to get job counts from Gitlab."""

    def api_url(self, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/api/v4/projects/{self.request.query.project_id}/"
                   f"jobs?private_token={self.request.query.private_token}")

    @classmethod
    def parse_source_response(cls, metric: str, response: requests.Response) -> Measurement:
        jobs = response.json()
        if metric == "failed_jobs":
            jobs = [job for job in jobs if job["status"] == "failed"]
        return Measurement(len(jobs))


class Gitlab(Source):
    """Gitlab source."""

    def get(self, metric: str) -> MeasurementResponse:
        delegate = dict(version=GitlabVersion).get(metric, GitlabJobs)
        return delegate(self.request).get(metric)
