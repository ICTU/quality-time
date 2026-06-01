"""Unit tests for token authentication source collectors."""

import unittest

from base_collectors import TokenAuthenticationSourceCollector
from source_collectors.bitbucket.base import BitbucketBase
from source_collectors.dependency_track.base import DependencyTrackBase
from source_collectors.github.base import GitHubBase
from source_collectors.gitlab.base import GitLabBase
from source_collectors.jira.base import JiraBase


class TokenAuthenticationSourceCollectorTest(unittest.TestCase):
    """Unit tests for passing a private token in a request header."""

    class FakeCollector(TokenAuthenticationSourceCollector):
        """Minimal collector that returns a fixed private token, without needing the data model."""

        AUTH_HEADER = "X-Custom-Header"
        AUTH_PREFIX = "Prefix "

        def __init__(self, credential: str = "") -> None:
            self.credential = credential

        def _parameter(self, parameter_key: str, quote: bool = False) -> str | list[str]:
            """Override to return the fixed credential, ignoring the parameter key."""
            return self.credential

    def test_header_with_token(self):
        """Test that the token is added to the configured header with the configured prefix."""
        self.assertEqual({"X-Custom-Header": "Prefix abc"}, self.FakeCollector("abc")._headers())  # noqa: SLF001

    def test_no_header_without_token(self):
        """Test that no header is added when no token is configured."""
        self.assertEqual({}, self.FakeCollector()._headers())  # noqa: SLF001

    def test_source_collector_token_configuration(self):
        """Test that each source collector passes its token in the expected header with the expected prefix."""
        self.assertEqual(("Private-Token", ""), (GitLabBase.AUTH_HEADER, GitLabBase.AUTH_PREFIX))
        self.assertEqual(("Authorization", "bearer "), (GitHubBase.AUTH_HEADER, GitHubBase.AUTH_PREFIX))
        self.assertEqual(("Authorization", "Bearer "), (BitbucketBase.AUTH_HEADER, BitbucketBase.AUTH_PREFIX))
        self.assertEqual(("Authorization", "Bearer "), (JiraBase.AUTH_HEADER, JiraBase.AUTH_PREFIX))
        self.assertEqual(("X-Api-Key", ""), (DependencyTrackBase.AUTH_HEADER, DependencyTrackBase.AUTH_PREFIX))
