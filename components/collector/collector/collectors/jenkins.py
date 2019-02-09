"""Jenkins metric collector."""

import requests

from collector.collector import Collector
from collector.type import Measurement, Units, URL


class JenkinsVersion(Collector):
    """Return the Jenkins version."""

    def parse_source_response(self, response: requests.Response) -> Measurement:
        return Measurement(response.headers["X-Jenkins"])


class JenkinsJobs(Collector):
    """Collector to get job counts from Jenkins."""

    def api_url(self, **parameters) -> URL:
        return URL(f"{parameters.get('url')}/api/json?tree=jobs[buildable,color,url,name]")

    def parse_source_response(self, response: requests.Response) -> Measurement:
        return Measurement(len(self.jobs(response)))

    def parse_source_response_units(self, source, response: requests.Response) -> Units:  # pylint: disable=no-self-use
        return [dict(key=unit["name"], name=unit["name"], url=unit["url"]) for unit in self.jobs(response)]

    @staticmethod
    def jobs(response: requests.Response) -> Units:
        """Return the jobs from the response that are buildable."""
        return [job for job in response.json()["jobs"] if job.get("buildable", False)]


class JenkinsFailedJobs(JenkinsJobs):
    """Collector to get failed job counts from Jenkins."""

    def parse_source_response(self, response: requests.Response) -> Measurement:
        jobs = [job for job in self.jobs(response) if not job.get("color", "").startswith("blue")]
        return Measurement(len(jobs))
