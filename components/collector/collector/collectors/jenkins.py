"""Jenkins metric collector."""

from datetime import datetime, timedelta

import requests

from collector.collector import Collector
from collector.type import Units, URL, Value


class JenkinsJobs(Collector):
    """Collector to get job counts from Jenkins."""

    def api_url(self, **parameters) -> URL:
        return URL(f"{parameters.get('url')}/api/json?tree=jobs[buildable,color,url,name,builds[result,timestamp]]")

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(len(self.jobs(response, **parameters)))

    def parse_source_response_units(self, response: requests.Response, **parameters) -> Units:
        return [
            dict(
                key=job["name"], name=job["name"], url=job["url"], build_status=self.build_status(job),
                build_age=str(self.build_age(job).days) if self.build_age(job) < timedelta.max else "",
                build_datetime=str(self.build_datetime(job).date()) if self.build_datetime(job) > datetime.min else "")
            for job in self.jobs(response, **parameters)]

    def jobs(self, response: requests.Response, **parameters):
        """Return the jobs from the response that are buildable."""
        return [job for job in response.json()["jobs"]
                if job.get("buildable") and self.count_job(job, **parameters)]

    def count_job(self, job, **parameters) -> bool:
        """Return whether the job should be counted."""
        raise NotImplementedError  # pragma: nocover

    def build_age(self, job) -> timedelta:
        """Return the age of the most recent build of the job."""
        build_datetime = self.build_datetime(job)
        return datetime.now() - build_datetime if build_datetime > datetime.min else timedelta.max

    @staticmethod
    def build_datetime(job) -> datetime:
        """Return the date and time of the most recent build of the job."""
        builds = job.get("builds")
        return datetime.utcfromtimestamp(int(builds[0]["timestamp"]) / 1000.) if builds else datetime.min

    @staticmethod
    def build_status(job) -> str:
        """Return the build status of the job."""
        builds = job.get("builds")
        return builds[0].get("result", "").capitalize().replace("_", " ") if builds else "Not built"


class JenkinsFailedJobs(JenkinsJobs):
    """Collector to get failed jobs from Jenkins."""

    def count_job(self, job, **parameters) -> bool:
        """Count the job if it's not successful (blue)."""
        return not job.get("color", "").startswith("blue")


class JenkinsUnusedJobs(JenkinsJobs):
    """Collector to get unused jobs from Jenkins."""

    def count_job(self, job, **parameters) -> bool:
        """Count the job if its most recent build is too old."""
        age = self.build_age(job)
        max_days = int(parameters.get("inactive_days", 0))
        return age > timedelta(days=max_days) if age < timedelta.max else False
