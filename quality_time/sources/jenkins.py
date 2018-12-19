"""Jenkins metric source."""

import requests

from quality_time.source import Source
from quality_time.type import Measurement, URL


class Jenkins(Source):
    """Base class for Jenkins metrics."""

    name = "Jenkins"


class JenkinsVersion(Jenkins):
    """Return the Jenkins version."""

    def parse_source_response(self, response: requests.Response) -> Measurement:
        return Measurement(response.headers["X-Jenkins"])


class JenkinsJobs(Jenkins):
    """Source class to get job counts from Jenkins."""

    def api_url(self, url: URL, component: str) -> URL:
        return URL(f"{url}/api/json?tree=jobs[buildable,color]")

    def parse_source_response(self, response: requests.Response) -> Measurement:
        jobs = [job for job in response.json()["jobs"] if job.get("buildable", False)]
        return Measurement(len(jobs))


class JenkinsFailedJobs(JenkinsJobs):
    """Source class to get failed job counts from Jenkins."""

    def parse_source_response(self, response: requests.Response) -> Measurement:
        jobs = [job for job in response.json()["jobs"] if job.get("buildable", False)]
        jobs = [job for job in jobs if not job.get("color", "").startswith("blue")]
        return Measurement(len(jobs))
