"""Jenkins metric source."""

from typing import Sequence

import requests

from quality_time.source import Source
from quality_time.type import Measurement, MeasurementResponse, URL


class _Jenkins(Source):
    """Base class for metric-specific Jenkins sources."""

    @classmethod
    def name(cls):
        return "Jenkins"


class JenkinsVersion(_Jenkins):
    """Return the Jenkins version."""

    @classmethod
    def parse_source_response(cls, metric: str, response: requests.Response) -> Measurement:
        return Measurement(response.headers["X-Jenkins"])


class JenkinsJobs(_Jenkins):
    """Source class to get job counts from Jenkins."""

    @classmethod
    def api_url(cls, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/api/json?tree=jobs[buildable,color]")

    @classmethod
    def parse_source_response(cls, metric: str, response: requests.Response) -> Measurement:
        jobs = [job for job in response.json()["jobs"] if job.get("buildable", False)]
        if metric == "failed_jobs":
            jobs = [job for job in jobs if not job.get("color", "").startswith("blue")]
        return Measurement(len(jobs))


class Jenkins(Source):
    """Jenkins source."""

    @classmethod
    def get(cls, metric: str, urls: Sequence[URL], components: Sequence[str]) -> MeasurementResponse:
        delegate = dict(version=JenkinsVersion).get(metric, JenkinsJobs)
        return delegate.get(metric, urls, components)
