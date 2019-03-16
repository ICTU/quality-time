"""Jenkins metric collector."""

from datetime import datetime, timedelta
from typing import Optional

import requests

from collector.collector import Collector
from collector.type import Units, URL, Value


class JenkinsJobs(Collector):
    """Collector to get job counts from Jenkins."""

    def api_url(self, **parameters) -> URL:
        return URL(f"{parameters.get('url')}/api/json?tree=jobs[buildable,color,url,name,builds[timestamp]]")

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(len(self.jobs(response)))

    def parse_source_response_units(self, response: requests.Response, **parameters) -> Units:
        return [dict(key=job["name"], name=job["name"], url=job["url"],
                     datetime=str(self.datetime(job).date())) for job in self.jobs(response)]

    def jobs(self, response: requests.Response):
        """Return the jobs from the response that are buildable."""
        return [job for job in response.json()["jobs"] if job.get("buildable", False) and self.count_job(job)]

    def count_job(self, job) -> bool:  # pylint: disable=no-self-use,unused-argument
        """Return whether the job should be counted."""
        return True

    @staticmethod
    def datetime(job) -> Optional[datetime]:
        """Return the date and time of the most recent build of the job."""
        builds = job.get("builds")
        return datetime.utcfromtimestamp(int(builds[0]["timestamp"])/1000.) if builds else None


class JenkinsFailedJobs(JenkinsJobs):
    """Collector to get failed jobs from Jenkins."""

    def count_job(self, job) -> bool:
        """Count the job if it's not successful (blue)."""
        return not job.get("color", "").startswith("blue")


class JenkinsUnusedJobs(JenkinsJobs):
    """Collector to get unused jobs from Jenkins."""

    def count_job(self, job) -> bool:
        """Count the job if it's most recent build is too old."""
        build_datetime = self.datetime(job)
        return datetime.now() - build_datetime > timedelta(days=10) if build_datetime else False
