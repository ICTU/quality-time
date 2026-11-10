"""Unit tests for the types."""

import unittest

from collector_utilities.type import URL


class URLTest(unittest.TestCase):
    """Unit tests for the URL class."""

    def test_is_str(self):
        """Test that a URL is a string."""
        self.assertEqual("https://example.org", URL("https://example.org"))

    def test_join(self):
        """Test that a path can be joined to a URL."""
        self.assertEqual("https://example.org/api", URL("https://example.org") / "api")

    def test_join_returns_url(self):
        """Test that joining a path to a URL returns a URL."""
        self.assertIsInstance(URL("https://example.org") / "api", URL)

    def test_join_url_with_trailing_slash(self):
        """Test that joining a path to a URL with a trailing slash does not result in a duplicate slash."""
        self.assertEqual("https://example.org/api", URL("https://example.org/") / "api")

    def test_join_path_with_leading_slash(self):
        """Test that joining a path with a leading slash does not result in a duplicate slash."""
        self.assertEqual("https://example.org/api", URL("https://example.org") / "/api")

    def test_join_url_with_trailing_slash_and_path_with_leading_slash(self):
        """Test that joining a path with a leading slash to a URL with a trailing slash results in one slash."""
        self.assertEqual("https://example.org/api", URL("https://example.org//") / "//api")

    def test_join_path_with_trailing_slash(self):
        """Test that a trailing slash of the path is kept."""
        self.assertEqual("https://example.org/api/", URL("https://example.org") / "api/")

    def test_join_multiple_segments(self):
        """Test that a path with multiple segments can be joined to a URL."""
        self.assertEqual("https://example.org/api/v4/projects", URL("https://example.org") / "api/v4/projects")

    def test_join_multiple_paths(self):
        """Test that multiple paths can be joined to a URL."""
        self.assertEqual("https://example.org/api/v4/projects", URL("https://example.org") / "api" / "v4" / "projects")

    def test_join_empty_path(self):
        """Test that joining an empty path returns the URL unchanged."""
        self.assertEqual("https://example.org/", URL("https://example.org/") / "")

    def test_join_path_to_empty_url(self):
        """Test that a path can be joined to an empty URL."""
        self.assertEqual("/api", URL("") / "api")

    def test_join_path_with_query(self):
        """Test that a path with a query string can be joined to a URL."""
        self.assertEqual("https://example.org/api?a=b", URL("https://example.org") / "api?a=b")

    def test_join_url_with_query(self):
        """Test that joining a path to a URL with a query string inserts the path before the query string."""
        self.assertEqual("https://example.org/api/v4?a=b/c", URL("https://example.org/api/?a=b/c") / "v4")

    def test_join_url_with_fragment(self):
        """Test that joining a path to a URL with a fragment inserts the path before the fragment."""
        self.assertEqual("https://example.org/api/v4#a/b", URL("https://example.org/api#a/b") / "v4")

    def test_join_url_with_query_and_fragment(self):
        """Test that joining a path to a URL with a query string and fragment inserts the path before both."""
        self.assertEqual("https://example.org/api/v4?a=b#c", URL("https://example.org/api?a=b#c") / "v4")

    def test_join_does_not_quote(self):
        """Test that joining a path does not quote or normalize the URL or the path."""
        self.assertEqual("https://example.org/a%2Fb/c d/../e", URL("https://example.org/a%2Fb") / "c d/../e")
