"""Base classes for Jenkins test report unit tests."""

from ...source_collector_test_case import SourceCollectorTestCase


class JenkinsTestReportTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Base class for Jenkins test report unit tests."""

    METRIC_TYPE = "subclass responsibility"

    def setUp(self):
        """Extend to set up the source fixture."""
        super().setUp()
        self.sources = dict(source_id=dict(type="jenkins_test_report", parameters=dict(url="https://jenkins/job")))
        self.metric = dict(type=self.METRIC_TYPE, addition="sum", sources=self.sources)
