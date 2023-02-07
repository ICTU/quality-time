"""Jenkins failed jobs collector."""

from model import Entity

from .base import JenkinsJobs


class JenkinsFailedJobs(JenkinsJobs):
    """Collector to get failed jobs from Jenkins."""

    def _include_entity(self, entity: Entity) -> bool:
        """Extend to count the job if its build status matches the failure types selected by the user."""
        return super()._include_entity(entity) and entity["build_status"] in self._parameter("failure_type")
