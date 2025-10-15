"""Jenkins CI-pipeline duration collector."""

from datetime import timedelta
from typing import TYPE_CHECKING, TypedDict, cast

from base_collectors import SourceCollector
from collector_utilities.date_time import minutes
from collector_utilities.functions import match_string_or_regular_expression
from collector_utilities.type import URL, Value

from .json_types import Build, Job

if TYPE_CHECKING:
    from collections.abc import Sequence

    from model import Entities, SourceResponses


class JSON(TypedDict):
    """Jenkins JSON."""

    builds: Sequence[Build]  # Workflow jobs have builds
    jobs: Sequence[Job]  # Multibranch pipelines have jobs that have builds


class JenkinsPipelineDuration(SourceCollector):
    """Jenkins CI-pipeline duration collector."""

    async def _api_url(self) -> URL:
        """Extend to add the job API path and parameters."""
        url = await super()._api_url()
        pipeline_job = self._parameter("pipeline")
        builds = "builds[duration,result,url]"
        # Add the builds parameter twice to get both builds of jobs as well as builds of multibranch pipelines:
        return URL(f"{url}/job/{pipeline_job}/api/json?tree=jobs[name,{builds}],{builds}")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to return the selected build as landing URL if the pipeline has any, or else the pipeline itself."""
        if build := await self._build(responses):
            return URL(build["url"])
        return URL(await super()._landing_url(responses) + f"/job/{self._parameter('pipeline')}")

    async def _parse_value(self, responses: SourceResponses, included_entities: Entities) -> Value:
        """Parse the value from the responses."""
        build = await self._build(responses)
        return str(minutes(timedelta(milliseconds=build["duration"]))) if build else "0"

    async def _build(self, responses: SourceResponses) -> Build | None:
        """Return the selected build, if any."""
        builds = [self._latest_build(job) for response in responses for job in self._jobs(await response.json())]
        builds = [build for build in builds if build is not None]
        return sorted(builds, key=lambda build: cast(Build, build)["duration"])[-1] if builds else None

    def _jobs(self, json: JSON) -> list[Job]:
        """Return the jobs in the Jenkins response."""
        return self._included_jobs(json["jobs"]) if "jobs" in json else [cast(Job, json)]

    def _included_jobs(self, jobs: Sequence[Job]) -> list[Job]:
        """Return the jobs that should be included."""
        return [job for job in jobs if self._include_branch(job["name"])]

    def _latest_build(self, job: Job) -> Build | None:
        """Return the latest build."""
        return next((build for build in job.get("builds", []) if self._include_build(build)), None)

    def _include_branch(self, branch: str) -> bool:
        """Return whether the branch should be considered."""
        if branches := self._parameter("branches"):
            return match_string_or_regular_expression(branch, branches)
        return True

    def _include_build(self, build: Build) -> bool:
        """Return whether the build should be included."""
        if build.get("building"):
            return False
        result_types = self._parameter("result_type")
        return str(build.get("result", "Not built")).capitalize().replace("_", " ") in result_types
