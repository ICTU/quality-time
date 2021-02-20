"""Base classes for Jenkins collector unit tests."""

from ..source_collector_test_case import SourceCollectorTestCase


class JenkinsTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Fixture for Jenkins unit tests."""

    SOURCE_TYPE = "jenkins"

    def setUp(self):
        """Extend to set up a Jenkins with a build."""
        super().setUp()
        self.set_source_parameter("failure_type", ["Failure"])
        self.builds = [dict(result="FAILURE", timestamp="1552686540953")]
        self.job_url = "https://job"
        self.job2_url = "https://job2"
