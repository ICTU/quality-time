"""Azure DevOps failed jobs collector."""

from model import Entity

from .base import AzureDevopsJobs


class AzureDevopsFailedJobs(AzureDevopsJobs):
    """Collector for the failed jobs metric."""

    def _include_entity(self, entity: Entity) -> bool:
        """Extend to check for failure type."""
        if not super()._include_entity(entity):
            return False
        return entity["build_status"] in self._parameter("failure_type")
