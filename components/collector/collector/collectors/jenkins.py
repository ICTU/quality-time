"""Jenkins metric collector."""

import requests

from collector.collector import Collector
from collector.type import Measurement, URL


class JenkinsVersion(Collector):
    """Return the Jenkins version."""

    def parse_source_response(self, response: requests.Response) -> Measurement:
        return Measurement(response.headers["X-Jenkins"])


class JenkinsJobs(Collector):
    """Collector to get job counts from Jenkins."""

    def api_url(self, source) -> URL:
        return URL(f"{source.get('url')}/api/json?tree=jobs[buildable,color]")

    def parse_source_response(self, response: requests.Response) -> Measurement:
        jobs = [job for job in response.json()["jobs"] if job.get("buildable", False)]
        return Measurement(len(jobs))


class JenkinsFailedJobs(JenkinsJobs):
    """Collector to get failed job counts from Jenkins."""

    def parse_source_response(self, response: requests.Response) -> Measurement:
        jobs = [job for job in response.json()["jobs"] if job.get("buildable", False)]
        jobs = [job for job in jobs if not job.get("color", "").startswith("blue")]
        return Measurement(len(jobs))
