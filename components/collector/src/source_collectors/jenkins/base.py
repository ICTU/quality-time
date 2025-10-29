"""Jenkins metric collector base classes."""

from typing import TYPE_CHECKING

from base_collectors import SourceCollector
from collector_utilities.date_time import datetime_from_timestamp
from collector_utilities.functions import match_string_or_regular_expression
from collector_utilities.type import URL
from model import Entities, Entity, SourceResponses

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

    from .json_types import Build, Job


class JenkinsJobs(SourceCollector):
    """Collector to get job counts from Jenkins."""

    async def _api_url(self) -> URL:
        """Extend to add the jobs API path and parameters."""
        url = await super()._api_url()
        job_attrs = "buildable,color,url,name,builds[duration,result,timestamp,url]"
        return URL(f"{url}/api/json?tree=jobs[{job_attrs},jobs[{job_attrs},jobs[{job_attrs}]]]")

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the jobs."""
        entities = Entities()
        for job in self._jobs((await responses[0].json())["jobs"]):
            builds = self._builds(job)
            build = builds[0]  # latest build
            job_build_datetime = datetime_from_timestamp(int(build["timestamp"])) if build else None
            job_build_date = str(job_build_datetime.date()) if job_build_datetime else ""
            job_build_duration = str(int(build["duration"] / 1000)) if build else ""
            job_build_url = build["url"] if build else job["url"]
            entities.append(
                Entity(
                    build_date=job_build_date,
                    build_datetime=job_build_datetime,
                    build_duration=job_build_duration,
                    build_result=self.__job_build_result(job),
                    key=job["name"],
                    name=job["name"],
                    url=job_build_url,
                )
            )
        return entities

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

    def _builds(self, job: Job) -> list[Build]:
        """Return the builds of the job."""
        return [build for build in job.get("builds", []) if self._include_build(build)]

    def _include_build(self, build: Build) -> bool:
        """Return whether to include this build or not."""
        return True

    def __job_build_result(self, job: Job) -> str:
        """Return the result of the most recent build of the job."""
        for build in self._builds(job):
            if "result" in build:
                return self._build_result(build)
        return "Not built"

    @staticmethod
    def _build_result(build: Build) -> str:
        """Return the result of the build."""
        return str(build.get("result", "Not built")).capitalize().replace("_", " ")
