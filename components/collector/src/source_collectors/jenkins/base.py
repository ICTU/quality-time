"""Jenkins metric collector base classes."""

from collections.abc import Iterator
from datetime import datetime

from base_collectors import SourceCollector
from collector_utilities.functions import match_string_or_regular_expression
from collector_utilities.type import URL, Job, Jobs
from source_model import Entity, SourceMeasurement, SourceResponses


class JenkinsJobs(SourceCollector):
    """Collector to get job counts from Jenkins."""

    async def _api_url(self) -> URL:
        """Extend to add the jobs API path and parameters."""
        url = await super()._api_url()
        job_attrs = "buildable,color,url,name,builds[result,timestamp]"
        return URL(f"{url}/api/json?tree=jobs[{job_attrs},jobs[{job_attrs},jobs[{job_attrs}]]]")

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the jobs."""
        entities = [
            Entity(
                key=job["name"],
                name=job["name"],
                url=job["url"],
                build_status=self._build_status(job),
                build_date=str(self._build_datetime(job).date()) if self._build_datetime(job) > datetime.min else "",
            )
            for job in self.__jobs((await responses[0].json())["jobs"])
        ]
        return SourceMeasurement(entities=entities)

    def __jobs(self, jobs: Jobs, parent_job_name: str = "") -> Iterator[Job]:
        """Recursively return the jobs and their child jobs that need to be counted for the metric."""
        for job in jobs:
            if parent_job_name:
                job["name"] = f"{parent_job_name}/{job['name']}"
            if job.get("buildable") and self._include_job(job):
                yield job
            for child_job in self.__jobs(job.get("jobs", []), parent_job_name=job["name"]):
                yield child_job

    def _include_job(self, job: Job) -> bool:
        """Return whether the job should be counted."""
        jobs_to_include = self._parameter("jobs_to_include")
        if len(jobs_to_include) > 0 and not match_string_or_regular_expression(job["name"], jobs_to_include):
            return False
        return not match_string_or_regular_expression(job["name"], self._parameter("jobs_to_ignore"))

    def _build_datetime(self, job: Job) -> datetime:
        """Return the date and time of the most recent build of the job."""
        builds = [build for build in job.get("builds", []) if self._include_build(build)]
        return datetime.utcfromtimestamp(int(builds[0]["timestamp"]) / 1000.0) if builds else datetime.min

    def _build_status(self, job: Job) -> str:
        """Return the status of the most recent build of the job."""
        builds = [build for build in job.get("builds", []) if self._include_build(build)]
        for build in builds:
            if status := build.get("result"):
                return str(status).capitalize().replace("_", " ")
        return "Not built"

    def _include_build(  # pylint: disable=no-self-use,unused-argument # skipcq: PYL-W0613,PYL-R0201
        self, build
    ) -> bool:
        """Return whether the include this build."""
        return True
