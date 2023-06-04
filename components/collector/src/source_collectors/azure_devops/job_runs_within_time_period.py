"""Azure DevOps Server pipeline runs within time period collector."""

from typing import cast

from collector_utilities.date_time import days_ago, parse_datetime
from model import Entity

from .base import AzureDevopsPipelines


class AzureDevopsJobRunsWithinTimePeriod(AzureDevopsPipelines):
    """Collector to count pipeline runs within time period from Azure Devops Server."""

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to include this run or not."""
        if not super()._include_entity(entity):
            return False

        return days_ago(parse_datetime(entity["build_date"])) <= int(cast(str, self._parameter("lookback_days")))
