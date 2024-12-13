"""Bitbucket unit test base classes."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class BitbucketTestCase(SourceCollectorTestCase):
    """Base class for testing Bitbucket collectors."""

    SOURCE_TYPE = "bitbucket"
    LOOKBACK_DAYS = "100000"

    def setUp(self):
        """Extend to add generic test fixtures."""
        super().setUp()
        self.set_source_parameter("branch", "branch")
        self.set_source_parameter("file_path", "file")
        self.set_source_parameter("lookback_days", self.LOOKBACK_DAYS)
        self.set_source_parameter("project", "namespace/project")