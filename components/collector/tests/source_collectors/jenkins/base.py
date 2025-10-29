"""Base classes for Jenkins collector unit tests."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class JenkinsTestCase(SourceCollectorTestCase):
    """Fixture for Jenkins unit tests."""

    SOURCE_TYPE = "jenkins"

    def setUp(self):
        """Extend to set up a Jenkins with a build."""
        super().setUp()
        self.set_source_parameter("failure_type", ["Failure"])
        self.job_url = "https://job"
        self.builds = [
            {"duration": "9001", "result": "FAILURE", "timestamp": 1552686540953, "url": f"{self.job_url}/4/"},
            {"duration": "42000", "result": "SUCCESS", "timestamp": 1552686531953, "url": f"{self.job_url}/3/"},
            {"duration": "0", "timestamp": 1552686531953, "url": f"{self.job_url}/2/"},
        ]
