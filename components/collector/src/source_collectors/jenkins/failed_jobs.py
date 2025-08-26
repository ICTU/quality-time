"""Jenkins failed jobs collector."""

from datetime import UTC, datetime, timedelta
from typing import cast

from collector_utilities.date_time import datetime_from_timestamp
from model import Entity

from .base import JenkinsJobs
from .json_types import Build


class JenkinsFailedJobs(JenkinsJobs):
    """Collector to get failed jobs from Jenkins."""

    def _include_entity(self, entity: Entity) -> bool:
        """Extend to count the job if its build status matches the failure types selected by the user."""
        return super()._include_entity(entity) and entity["build_result"] in self._parameter("failure_type")

    def _include_build(self, build: Build) -> bool:
        """Return whether to include this build or not."""
        if self._build_result(build) not in self._parameter("failure_type"):
            return True  # No need to apply the grace period to builds that have not failed
        grace_period = timedelta(days=int(cast(str, self._parameter("grace_days"))))
        build_age = datetime.now(tz=UTC) - datetime_from_timestamp(int(build["timestamp"]))
        return build_age > grace_period
