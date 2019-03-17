"""Jenkins metric collector."""

from datetime import datetime, timedelta

import requests

from collector.collector import Collector
from collector.type import Units, URL, Value


class JenkinsJobs(Collector):
    """Collector to get job counts from Jenkins."""

    def api_url(self, **parameters) -> URL:
        job_attrs = "buildable,color,url,name,builds[result,timestamp]"
        return URL(f"{parameters.get('url')}/api/json?tree=jobs[{job_attrs},jobs[{job_attrs},jobs[{job_attrs}]]]")

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(len(list(self.jobs(response.json()["jobs"], **parameters))))

    def parse_source_response_units(self, response: requests.Response, **parameters) -> Units:
        return [
            dict(
                key=job["name"], name=job["name"], url=job["url"], build_status=self.build_status(job),
                build_age=str(self.build_age(job).days) if self.build_age(job) < timedelta.max else "",
                build_datetime=str(self.build_datetime(job).date()) if self.build_datetime(job) > datetime.min else "")
            for job in self.jobs(response.json()["jobs"], **parameters)]

    def jobs(self, jobs, **parameters):
        """Recursively return the jobs and their child jobs that need to be counted for the metric."""
        for job in jobs:
            if job.get("buildable") and self.count_job(job, **parameters):
                yield job
            for child_job in self.jobs(job.get("jobs", []), **parameters):
                yield child_job

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
        if builds:
            status = builds[0].get("result")
            if status:
                return status.capitalize().replace("_", " ")
        return "Not built"


class JenkinsFailedJobs(JenkinsJobs):
    """Collector to get failed jobs from Jenkins."""

    def count_job(self, job, **parameters) -> bool:
        """Count the job if its build status matches the failure types selected by the user."""
        return self.build_status(job) in parameters.get("failure_type", [])


class JenkinsUnusedJobs(JenkinsJobs):
    """Collector to get unused jobs from Jenkins."""

    def count_job(self, job, **parameters) -> bool:
        """Count the job if its most recent build is too old."""
        age = self.build_age(job)
        max_days = int(parameters.get("inactive_days", 0))
        return age > timedelta(days=max_days) if age < timedelta.max else False
