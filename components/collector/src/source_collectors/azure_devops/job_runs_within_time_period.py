"""Azure DevOps Server pipeline runs within time period collector."""

from typing import cast

from dateutil.parser import parse

from collector_utilities.functions import days_ago
from collector_utilities.type import Job

from .base import AzureDevopsPipelines


class AzureDevopsJobRunsWithinTimePeriod(AzureDevopsPipelines):
    """Collector to count pipeline runs within time period from Azure Devops Server."""

    def _include_pipeline_run(self, job: Job) -> bool:
        """Return whether to include this run or not."""
        if not super()._include_pipeline_run(job):
            return False

        return days_ago(parse(job["finishedDate"])) <= int(cast(str, self._parameter(parameter_key="lookback_days")))
