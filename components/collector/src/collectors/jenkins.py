"""Jenkins metric collector."""

from datetime import datetime, timedelta
from typing import cast, Iterator, List

import requests

from ..collector import Collector
from ..type import Job, Jobs, Entities, URL, Value


class JenkinsJobs(Collector):
    """Collector to get job counts from Jenkins."""

    def api_url(self) -> URL:
        url = super().api_url()
        job_attrs = "buildable,color,url,name,builds[result,timestamp]"
        return URL(f"{url}/api/json?tree=jobs[{job_attrs},jobs[{job_attrs},jobs[{job_attrs}]]]")

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        return str(len(list(self.jobs(responses[0].json()["jobs"]))))

    def parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        return [
            dict(
                key=job["name"], name=job["name"], url=job["url"], build_status=self.build_status(job),
                build_age=str(self.build_age(job).days) if self.build_age(job) < timedelta.max else "",
                build_date=str(self.build_datetime(job).date()) if self.build_datetime(job) > datetime.min else "")
            for job in self.jobs(responses[0].json()["jobs"])]

    def jobs(self, jobs: Jobs) -> Iterator[Job]:
        """Recursively return the jobs and their child jobs that need to be counted for the metric."""
        for job in jobs:
            if job.get("buildable") and self.count_job(job):
                yield job
            for child_job in self.jobs(job.get("jobs", [])):
                yield child_job

    def count_job(self, job: Job) -> bool:
        """Return whether the job should be counted."""
        raise NotImplementedError  # pragma: nocover

    def build_age(self, job: Job) -> timedelta:
        """Return the age of the most recent build of the job."""
        build_datetime = self.build_datetime(job)
        return datetime.now() - build_datetime if build_datetime > datetime.min else timedelta.max

    @staticmethod
    def build_datetime(job: Job) -> datetime:
        """Return the date and time of the most recent build of the job."""
        builds = job.get("builds")
        return datetime.utcfromtimestamp(int(builds[0]["timestamp"]) / 1000.) if builds else datetime.min

    @staticmethod
    def build_status(job: Job) -> str:
        """Return the build status of the job."""
        builds = job.get("builds")
        if builds:
            status = builds[0].get("result")
            if status:
                return status.capitalize().replace("_", " ")
        return "Not built"


class JenkinsFailedJobs(JenkinsJobs):
    """Collector to get failed jobs from Jenkins."""

    def count_job(self, job: Job) -> bool:
        """Count the job if its build status matches the failure types selected by the user."""
        return self.build_status(job) in self.parameters.get("failure_type", [])


class JenkinsUnusedJobs(JenkinsJobs):
    """Collector to get unused jobs from Jenkins."""

    def count_job(self, job: Job) -> bool:
        """Count the job if its most recent build is too old."""
        age = self.build_age(job)
        max_days = int(cast(str, self.parameters.get("inactive_days", "0")))
        return age > timedelta(days=max_days) if age < timedelta.max else False
