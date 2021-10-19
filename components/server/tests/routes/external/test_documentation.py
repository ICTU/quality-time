"""Unit tests for the reports routes."""

import unittest

from routes.external import get_api


class DocumentationTest(unittest.TestCase):
    """Unit tests for the documentation routes."""

    login_v2 = "/api/v2/login"
    login_v3 = "/api/v3/login"
    logout_v2 = "/api/v2/logout"
    logout_v3 = "/api/v3/logout"

    def test_get_api(self):
        """Test that the API can be retrieved."""
        api_json = get_api()
        self.assertTrue("/api" in api_json)
        self.assertFalse(self.login_v2 in api_json)
        self.assertTrue(self.login_v3 in api_json)
        self.assertFalse(self.logout_v2 in api_json)
        self.assertTrue(self.logout_v3 in api_json)

    def test_get_api_by_version(self):
        """Test that the API can be filtered by version."""
        api_json = get_api("v3")
        self.assertFalse(self.login_v2 in api_json)
        self.assertTrue(self.login_v3 in api_json)

    def test_get_api_by_fragment(self):
        """Test that the API can be filtered by version and a fragment."""
        api_json = get_api("v3", "logout")
        self.assertFalse(self.login_v3 in api_json)
        self.assertTrue(self.logout_v3 in api_json)
