"""Base class for Checkmarx CxSAST collector unit tests."""

from ...source_collector_test_case import SourceCollectorTestCase


class CxSASTTestCase(SourceCollectorTestCase):
    """Base class for testing CxSAST collectors."""

    def setUp(self):
        """Extend to add a CxSAST source fixture."""
        super().setUp()
        self.sources = dict(
            source_id=dict(
                type="cxsast",
                parameters=dict(url="https://checkmarx/", username="user", password="pass", project="project"),
            )
        )
