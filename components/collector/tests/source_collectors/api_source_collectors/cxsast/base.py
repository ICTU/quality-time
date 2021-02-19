"""Base class for Checkmarx CxSAST collector unit tests."""

from ...source_collector_test_case import SourceCollectorTestCase


class CxSASTTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Base class for testing CxSAST collectors."""

    SOURCE_TYPE = "cxsast"

    def setUp(self):
        """Extend to add a CxSAST source fixture."""
        super().setUp()
        self.sources["source_id"]["parameters"]["project"] = "project"
