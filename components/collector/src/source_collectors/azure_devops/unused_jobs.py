"""Azure DevOps unused jobs collector."""

from typing import cast

from collector_utilities.date_time import days_ago, parse_datetime
from model import Entity

from .base import AzureDevopsJobs


class AzureDevopsUnusedJobs(AzureDevopsJobs):
    """Collector for the unused jobs metric."""

    def _include_entity(self, entity: Entity) -> bool:
        """Extend to filter unused jobs."""
        if not super()._include_entity(entity):
            return False
        max_days = int(cast(str, self._parameter("inactive_job_days")))
        if not (build_date := entity["build_date"]):
            return False
        actual_days = days_ago(parse_datetime(build_date))
        return actual_days > max_days
