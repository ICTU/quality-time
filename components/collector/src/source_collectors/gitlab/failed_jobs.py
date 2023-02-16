"""GitLab failed jobs collector."""

from model import Entity

from .base import GitLabJobsBase


class GitLabFailedJobs(GitLabJobsBase):
    """Collector class to get failed job counts from GitLab."""

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether the job has failed."""
        failure_types = list(self._parameter("failure_type"))
        return super()._include_entity(entity) and entity["build_status"] in failure_types
