"""Jenkins change failure rate deploys collector."""

from typing import TYPE_CHECKING, cast

from collector_utilities.date_time import datetime_from_timestamp, days_ago
from model import Entities, Entity, SourceResponses

from .base import JenkinsJobs

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

    from .json_types import Build, Job


class JenkinsChangeFailureRate(JenkinsJobs):
    """Collector to get change failure rate from Jenkins."""

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to include this build or not."""
        if not super()._include_entity(entity):
            return False
        return days_ago(entity["build_datetime"]) <= int(cast(str, self._parameter("lookback_days")))

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the jobs."""
        return Entities(
            [
                Entity(
                    build_date=str(datetime_from_timestamp(build["timestamp"])),
                    build_datetime=datetime_from_timestamp(build["timestamp"]),
                    build_result=str(build.get("result", "")).capitalize().replace("_", " "),
                    key=f"{job['name']}-{build['timestamp']}",
                    name=job["name"],
                    url=job["url"],
                )
                for build, job in self._builds_with_jobs((await responses[0].json())["jobs"])
            ],
        )

    def _builds_with_jobs(self, jobs: Sequence[Job]) -> Iterator[tuple[Build, Job]]:
        """Recursively return the builds and their respective jobs, for all selected jobs."""
        for job in self._jobs(jobs):
            for build in job.get("builds", []):
                if self._include_build(build):  # pragma: no cover # can be overridden
                    yield build, job
