"""GitLab failed jobs collector."""

from typing import TYPE_CHECKING

from collector_utilities.type import URL

from .base import GitLabJobsBase

if TYPE_CHECKING:
    from model import Entity


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
