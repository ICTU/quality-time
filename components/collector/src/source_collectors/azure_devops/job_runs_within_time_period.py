"""Azure DevOps Server pipeline runs within time period collector."""

from typing import TYPE_CHECKING, cast

from collector_utilities.date_time import days_ago, parse_datetime

from .base import AzureDevopsPipelines

if TYPE_CHECKING:
    from model import Entity


class AzureDevopsJobRunsWithinTimePeriod(AzureDevopsPipelines):
    """Collector to count pipeline runs within time period from Azure Devops Server."""

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to include this run or not."""
        if not super()._include_entity(entity):
            return False
        build_age = days_ago(parse_datetime(entity["build_date"]))
        max_build_age = int(cast(str, self._parameter("lookback_days_pipeline_runs")))
        result_types = cast(list[str], self._parameter("result_type"))
        return build_age <= max_build_age and entity["build_result"] in result_types
