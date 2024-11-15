"""GitLab failed jobs collector."""

from collector_utilities.type import URL
from model import Entity

from .base import GitLabJobsBase


class GitLabFailedJobs(GitLabJobsBase):
    """Collector class to get failed job counts from GitLab."""

    async def _api_url(self) -> URL:
        """Extend to add the scope parameter of the jobs API."""
        failure_types = list(self._parameter("failure_type"))
        scopes = "&".join([f"scope[]={failure_type}" for failure_type in failure_types])
        return URL(f"{await super()._api_url()}&{scopes}")

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether the job has failed."""
        failure_types = list(self._parameter("failure_type"))
        return super()._include_entity(entity) and entity["build_result"] in failure_types
