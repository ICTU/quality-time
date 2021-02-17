"""Base class for Bandit unit tests."""

from ...source_collector_test_case import SourceCollectorTestCase


class BanditTestCase(SourceCollectorTestCase):
    """Base class for testing Bandit collectors."""

    METRIC_TYPE = "Subclass responsibility"
    METRIC_ADDITION = "sum"

    def setUp(self):
        """Extend to create source and metric fixtures."""
        super().setUp()
        self.sources = dict(source_id=dict(type="bandit", parameters=dict(url="bandit.json")))
        self.metric = dict(type=self.METRIC_TYPE, sources=self.sources, addition=self.METRIC_ADDITION)
