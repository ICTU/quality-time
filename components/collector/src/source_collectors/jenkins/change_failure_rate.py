"""Jenkins change failure rate deploys collector."""

from collections.abc import Iterator
from typing import cast

from collector_utilities.date_time import datetime_from_timestamp, days_ago, parse_datetime
from collector_utilities.type import Build, Job, Jobs
from model import Entities, Entity, SourceResponses

from .base import JenkinsJobs


class JenkinsChangeFailureRate(JenkinsJobs):
    """Collector to get change failure rate from Jenkins."""

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to include this build or not."""
        if not super()._include_entity(entity):
            return False
        build_datetime = parse_datetime(entity["build_date"])
        return days_ago(build_datetime) <= int(cast(str, self._parameter("lookback_days")))

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the jobs."""
        return Entities(
            [
                Entity(
                    key=f"{job['name']}-{build['timestamp']}",
                    name=job["name"],
                    url=job["url"],
                    build_status=str(build.get("result", "")).capitalize().replace("_", " "),
                    build_date=str(datetime_from_timestamp(int(cast(int, build["timestamp"])))),
                )
                for build, job in self._builds_with_jobs((await responses[0].json())["jobs"])
            ],
        )

    def _builds_with_jobs(self, jobs: Jobs) -> Iterator[tuple[Build, Job]]:
        """Recursively return the builds and their respective jobs, for all selected jobs."""
        for job in self._jobs(jobs):
            for build in job.get("builds", []):
                if self._include_build(build):  # pragma: no cover # can be overridden
                    yield build, job
