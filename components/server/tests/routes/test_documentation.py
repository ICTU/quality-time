"""Unit tests for the reports routes."""

import unittest

from routes.documentation import get_api


class DocumentationTest(unittest.TestCase):
    """Unit tests for the documentation routes."""

    def test_get_api(self):
        """Test that the API can be retrieved."""
        api_json = get_api()
        self.assertTrue("/api" in api_json)
        self.assertTrue("/api/v1/login" in api_json)
        self.assertTrue("/api/v2/login" in api_json)
        self.assertTrue("/api/v1/logout" in api_json)
        self.assertTrue("/api/v2/logout" in api_json)

    def test_get_api_by_version(self):
        """Test that the API can be filtered by version."""
        api_json = get_api("v2")
        self.assertFalse("/api/v1/login" in api_json)
        self.assertTrue("/api/v2/login" in api_json)

    def test_get_api_by_fragment(self):
        """Test that the API can be filtered by version and a fragment."""
        api_json = get_api("v2", "logout")
        self.assertFalse("/api/v2/login" in api_json)
        self.assertTrue("/api/v2/logout" in api_json)
