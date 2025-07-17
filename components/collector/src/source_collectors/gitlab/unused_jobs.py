"""GitLab unused jobs collector."""

from typing import TYPE_CHECKING, cast

from collector_utilities.date_time import days_ago

from .base import GitLabJobsBase

if TYPE_CHECKING:
    from model import Entity


class GitLabUnusedJobs(GitLabJobsBase):
    """Collector class to get unused job counts from GitLab."""

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether the job is unused."""
        max_days = int(cast(str, self._parameter("inactive_job_days")))
        return super()._include_entity(entity) and days_ago(entity["build_datetime"]) > max_days
