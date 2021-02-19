"""Base classes for NCover collector unit tests."""

from ...source_collector_test_case import SourceCollectorTestCase


class NCoverTestCase(SourceCollectorTestCase):
    """Base class for NCover collector unit tests."""

    METRIC_TYPE = "Subclass responsibility"
    METRIC_ADDITION = "sum"

    def setUp(self):
        """Extend to set up the sources and metric under test."""
        super().setUp()
        self.sources = dict(source_id=dict(type="ncover", parameters=dict(url="https://ncover/report.html")))
        self.metric = dict(type=self.METRIC_TYPE, sources=self.sources, addition=self.METRIC_ADDITION)
