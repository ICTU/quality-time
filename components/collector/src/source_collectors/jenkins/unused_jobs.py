"""Jenkins unused jobs collector."""

from typing import cast

from dateutil.parser import parse

from collector_utilities.functions import days_ago
from model import Entity

from .base import JenkinsJobs


class JenkinsUnusedJobs(JenkinsJobs):
    """Collector to get unused jobs from Jenkins."""

    def _include_entity(self, entity: Entity) -> bool:
        """Extend to count the job if its most recent build is too old."""
        if not (build_date_str := entity["build_date"]):
            return False  # "build_date" is only set if self._build_datetime(job) > datetime.min
        max_days = int(cast(str, self._parameter("inactive_days")))
        return super()._include_entity(entity) and days_ago(parse(build_date_str)) > max_days
