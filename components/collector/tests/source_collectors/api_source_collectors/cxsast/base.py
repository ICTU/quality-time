"""Base class for Checkmarx CxSAST collector unit tests."""

from ...source_collector_test_case import SourceCollectorTestCase


class CxSASTTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Base class for testing CxSAST collectors."""

    METRIC_TYPE = "Subclass responsibility"
    METRIC_ADDITION = "sum"

    def setUp(self):
        """Extend to add a CxSAST source fixture."""
        super().setUp()
        self.sources = dict(
            source_id=dict(
                type="cxsast",
                parameters=dict(url="https://checkmarx/", username="user", password="pass", project="project"),
            )
        )
        self.metric = dict(type=self.METRIC_TYPE, sources=self.sources, addition=self.METRIC_ADDITION)
