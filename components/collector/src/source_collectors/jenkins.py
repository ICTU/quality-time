"""Jenkins metric collector."""

from datetime import datetime
from typing import cast, Iterator, Tuple

from collector_utilities.functions import days_ago, match_string_or_regular_expression
from collector_utilities.type import Job, Jobs, Entities, Responses, URL, Value
from .source_collector import SourceCollector


class JenkinsJobs(SourceCollector):
    """Collector to get job counts from Jenkins."""

    def _api_url(self) -> URL:
        url = super()._api_url()
        job_attrs = "buildable,color,url,name,builds[result,timestamp]"
        return URL(f"{url}/api/json?tree=jobs[{job_attrs},jobs[{job_attrs},jobs[{job_attrs}]]]")

    def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        entities = [
            dict(
                key=job["name"], name=job["name"], url=job["url"], build_status=self._build_status(job),
                build_age=str(days_ago(self._build_datetime(job))) if self._build_datetime(job) > datetime.min else "",
                build_date=str(self._build_datetime(job).date()) if self._build_datetime(job) > datetime.min else "")
            for job in self.__jobs(responses[0].json()["jobs"])]
        return str(len(entities)), "100", entities

    def __jobs(self, jobs: Jobs, parent_job_name: str = "") -> Iterator[Job]:
        """Recursively return the jobs and their child jobs that need to be counted for the metric."""
        for job in jobs:
            if parent_job_name:
                job["name"] = f"{parent_job_name}/{job['name']}"
            if job.get("buildable") and self._count_job(job):
                yield job
            for child_job in self.__jobs(job.get("jobs", []), parent_job_name=job["name"]):
                yield child_job

    def _count_job(self, job: Job) -> bool:
        """Return whether the job should be counted."""
        return not match_string_or_regular_expression(job["name"], self._parameter("jobs_to_ignore"))

    @staticmethod
    def _build_datetime(job: Job) -> datetime:
        """Return the date and time of the most recent build of the job."""
        builds = job.get("builds")
        return datetime.utcfromtimestamp(int(builds[0]["timestamp"]) / 1000.) if builds else datetime.min

    @staticmethod
    def _build_status(job: Job) -> str:
        """Return the build status of the job."""
        for build in job.get("builds", []):
            if status := build.get("result"):
                return str(status).capitalize().replace("_", " ")
        return "Not built"


class JenkinsFailedJobs(JenkinsJobs):
    """Collector to get failed jobs from Jenkins."""

    def _count_job(self, job: Job) -> bool:
        """Count the job if its build status matches the failure types selected by the user."""
        return super()._count_job(job) and self._build_status(job) in self._parameter("failure_type")


class JenkinsUnusedJobs(JenkinsJobs):
    """Collector to get unused jobs from Jenkins."""

    def _count_job(self, job: Job) -> bool:
        """Count the job if its most recent build is too old."""
        if super()._count_job(job) and (build_datetime := self._build_datetime(job)) > datetime.min:
            max_days = int(cast(str, self._parameter("inactive_days")))
            return days_ago(build_datetime) > max_days
        return False
