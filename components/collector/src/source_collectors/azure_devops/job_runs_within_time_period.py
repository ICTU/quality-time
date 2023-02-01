"""Azure DevOps Server pipeline runs within time period collector."""

from typing import cast

from dateutil.parser import parse

from collector_utilities.functions import days_ago
from model import Entity

from .base import AzureDevopsPipelines


class AzureDevopsJobRunsWithinTimePeriod(AzureDevopsPipelines):
    """Collector to count pipeline runs within time period from Azure Devops Server."""

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to include this run or not."""
        if not super()._include_entity(entity):
            return False

        return days_ago(parse(entity["build_date"])) <= int(cast(str, self._parameter("lookback_days")))
