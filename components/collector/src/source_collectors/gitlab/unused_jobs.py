"""GitLab unused jobs collector."""

from typing import cast

from dateutil.parser import parse

from collector_utilities.functions import days_ago
from model import Entity

from .base import GitLabJobsBase


class GitLabUnusedJobs(GitLabJobsBase):
    """Collector class to get unused job counts from GitLab."""

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether the job is unused."""
        max_days = int(cast(str, self._parameter("inactive_job_days")))
        return super()._include_entity(entity) and days_ago(parse(entity["build_date"])) > max_days
