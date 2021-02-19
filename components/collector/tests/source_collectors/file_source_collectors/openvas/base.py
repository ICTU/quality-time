"""Base classes for OpenVAS collector unit tests."""

from ...source_collector_test_case import SourceCollectorTestCase


class OpenVASTestCase(SourceCollectorTestCase):
    """Base class for NCover collector unit tests."""

    METRIC_TYPE = "Subclass responsibility"
    METRIC_ADDITION = "sum"

    def setUp(self):
        """Extend to set up the sources and metric under test."""
        super().setUp()
        self.sources = dict(source_id=dict(type="openvas", parameters=dict(url="https://openvas.xml")))
        self.metric = dict(type=self.METRIC_TYPE, sources=self.sources, addition=self.METRIC_ADDITION)
