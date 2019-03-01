"""Jenkins metric collector."""

import requests

from collector.collector import Collector
from collector.type import Units, URL, Value


class JenkinsJobs(Collector):
    """Collector to get job counts from Jenkins."""

    def api_url(self, **parameters) -> URL:
        return URL(f"{parameters.get('url')}/api/json?tree=jobs[buildable,color,url,name]")

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(len(self.jobs(response)))

    def parse_source_response_units(self, response: requests.Response, **parameters) -> Units:
        return [dict(key=job["name"], name=job["name"], url=job["url"]) for job in self.jobs(response)]

    @staticmethod
    def jobs(response: requests.Response):
        """Return the jobs from the response that are buildable."""
        return [job for job in response.json()["jobs"] if job.get("buildable", False)]


class JenkinsFailedJobs(JenkinsJobs):
    """Collector to get failed job counts from Jenkins."""

    @staticmethod
    def jobs(response: requests.Response):
        """Return the jobs from the response that have failed."""
        return [job for job in super().jobs(response) if not job.get("color", "").startswith("blue")]
