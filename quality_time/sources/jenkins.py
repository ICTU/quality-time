"""Jenkins metric source."""

import requests

from quality_time.source import Source
from quality_time.type import Measurement, MeasurementResponse, URL


class JenkinsVersion(Source):
    """Return the Jenkins version."""

    def parse_source_response(self, metric: str, response: requests.Response) -> Measurement:
        return Measurement(response.headers["X-Jenkins"])


class JenkinsJobs(Source):
    """Source class to get job counts from Jenkins."""

    def api_url(self, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/api/json?tree=jobs[buildable,color]")

    def parse_source_response(self, metric: str, response: requests.Response) -> Measurement:
        jobs = [job for job in response.json()["jobs"] if job.get("buildable", False)]
        if metric == "failed_jobs":
            jobs = [job for job in jobs if not job.get("color", "").startswith("blue")]
        return Measurement(len(jobs))


class Jenkins(Source):
    """Jenkins source."""

    def get(self, metric: str) -> MeasurementResponse:
        delegate = dict(version=JenkinsVersion).get(metric, JenkinsJobs)
        return delegate(self.request).get(metric)
