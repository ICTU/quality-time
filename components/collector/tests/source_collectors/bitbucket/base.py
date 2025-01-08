"""Bitbucket unit test base classes."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class BitbucketTestCase(SourceCollectorTestCase):
    """Base class for testing Bitbucket collectors."""

    SOURCE_TYPE = "bitbucket"

    def setUp(self):
        """Extend to add generic test fixtures."""
        super().setUp()
        self.set_source_parameter("branch", "branch")
        self.set_source_parameter("owner", "owner")
        self.set_source_parameter("repository", "repository")
