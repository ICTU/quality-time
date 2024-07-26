"""GitHub unit test base classes."""
# Author: Tobias Termeczky
# Company: the/experts.

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class GitHubTestCase(SourceCollectorTestCase):
    """Base class for testing GitHub collectors."""

    SOURCE_TYPE = "github"

    def setUp(self):
        """Extend to add generic test fixtures."""
        super().setUp()
        self.set_source_parameter("branch", "branch")
        self.set_source_parameter("owner", "owner")
        self.set_source_parameter("repository", "repository")
