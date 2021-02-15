"""Base classes for Jenkins collector unit tests."""

from ...source_collector_test_case import SourceCollectorTestCase


class JenkinsTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Fixture for Jenkins unit tests."""

    METRIC_TYPE = "subclass responsibility"
    ADDITION = "sum"

    def setUp(self):
        """Extend to set up a Jenkins with a build."""
        super().setUp()
        self.sources = dict(
            source_id=dict(type="jenkins", parameters=dict(url="https://jenkins/", failure_type=["Failure"]))
        )
        self.metric = dict(type=self.METRIC_TYPE, sources=self.sources, addition=self.ADDITION)
        self.builds = [dict(result="FAILURE", timestamp="1552686540953")]
        self.job_url = "https://job"
        self.job2_url = "https://job2"
