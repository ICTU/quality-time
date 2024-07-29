"""Jenkins metric collector base classes."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from base_collectors import SourceCollector
from collector_utilities.date_time import datetime_from_timestamp
from collector_utilities.functions import match_string_or_regular_expression
from collector_utilities.type import URL
from model import Entities, Entity, SourceResponses

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence


class Build(TypedDict):
    """Jenkins build."""

    result: str
    timestamp: str


class Job(TypedDict):
    """Jenkins job."""

    buildable: bool
    builds: Sequence[Build]
    jobs: Sequence[Job]
    name: str
    url: str


class JenkinsJobs(SourceCollector):
    """Collector to get job counts from Jenkins."""

    async def _api_url(self) -> URL:
        """Extend to add the jobs API path and parameters."""
        url = await super()._api_url()
        job_attrs = "buildable,color,url,name,builds[result,timestamp]"
        return URL(f"{url}/api/json?tree=jobs[{job_attrs},jobs[{job_attrs},jobs[{job_attrs}]]]")

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the jobs."""
        return Entities(
            [
                Entity(
                    key=job["name"],
                    name=job["name"],
                    url=job["url"],
                    build_status=self._build_status(job),
                    build_date=self._build_date(job),
                )
                for job in self._jobs((await responses[0].json())["jobs"])
            ],
        )

    def _jobs(self, jobs: Sequence[Job], parent_job_name: str = "") -> Iterator[Job]:
        """Recursively return the jobs and their child jobs that need to be counted for the metric."""
        for job in jobs:
            if parent_job_name:
                job["name"] = f"{parent_job_name}/{job['name']}"
            if job.get("buildable"):
                yield job
            yield from self._jobs(job.get("jobs", []), parent_job_name=job["name"])

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether the job should be counted."""
        jobs_to_include = self._parameter("jobs_to_include")
        if len(jobs_to_include) > 0 and not match_string_or_regular_expression(entity["name"], jobs_to_include):
            return False
        return not match_string_or_regular_expression(entity["name"], self._parameter("jobs_to_ignore"))

    def _build_date(self, job: Job) -> str:
        """Return the date of the most recent build of the job."""
        builds = self._builds(job)
        if builds:
            build_datetime = datetime_from_timestamp(int(builds[0]["timestamp"]))
            return str(build_datetime.date())
        return ""

    def _build_status(self, job: Job) -> str:
        """Return the status of the most recent build of the job."""
        for build in self._builds(job):
            if status := build.get("result"):
                return str(status).capitalize().replace("_", " ")
        return "Not built"

    def _builds(self, job: Job) -> list[Build]:
        """Return the builds of the job."""
        return [build for build in job.get("builds", []) if self._include_build(build)]

    def _include_build(self, build: Build) -> bool:
        """Return whether to include this build or not."""
        return True
