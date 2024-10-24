"""Jenkins unused jobs collector."""

from typing import cast

from collector_utilities.date_time import days_ago
from model import Entity

from .base import JenkinsJobs


class JenkinsUnusedJobs(JenkinsJobs):
    """Collector to get unused jobs from Jenkins."""

    def _include_entity(self, entity: Entity) -> bool:
        """Extend to count the job if its most recent build is too old."""
        if not (build_datetime := entity["build_datetime"]):
            return False
        max_days = int(cast(str, self._parameter("inactive_days")))
        return super()._include_entity(entity) and days_ago(build_datetime) > max_days
