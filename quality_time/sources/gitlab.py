"""Gitlab metric source."""

from typing import Sequence

import requests
from bottle import request

from quality_time.source import Source
from quality_time.type import Measurement, MeasurementResponse, URL


class _Gitlab(Source):
    """Base class for metric-specific Gitlab sources."""

    @classmethod
    def name(cls):
        return "Gitlab"


class GitlabVersion(_Gitlab):
    """Return the Gitlab version."""

    @classmethod
    def api_url(cls, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/api/v4/version?private_token={request.query.private_token}")  # pylint: disable=no-member

    @classmethod
    def parse_source_response(cls, metric: str, response: requests.Response) -> Measurement:
        return Measurement(response.json()["version"])


class GitlabJobs(_Gitlab):
    """Source class to get job counts from Gitlab."""

    @classmethod
    def api_url(cls, metric: str, url: URL, component: str) -> URL:
        # pylint: disable=no-member
        return URL(f"{url}/api/v4/projects/{request.query.project_id}/jobs?private_token={request.query.private_token}")

    @classmethod
    def parse_source_response(cls, metric: str, response: requests.Response) -> Measurement:
        jobs = response.json()
        if metric == "failed_jobs":
            jobs = [job for job in jobs if job["status"] == "failed"]
        return Measurement(len(jobs))


class Gitlab(Source):
    """Gitlab source."""

    @classmethod
    def get(cls, metric: str, urls: Sequence[URL], components: Sequence[str]) -> MeasurementResponse:
        delegate = dict(version=GitlabVersion).get(metric, GitlabJobs)
        return delegate.get(metric, urls, components)
