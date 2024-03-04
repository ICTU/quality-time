"""Unit tests for the reports routes."""

import unittest

from routes import get_api


class DocumentationTest(unittest.TestCase):
    """Unit tests for the documentation routes."""

    login_v2 = "/api/v2/login"
    login_v3 = "/api/v3/login"
    logout_v2 = "/api/v2/logout"
    logout_v3 = "/api/v3/logout"

    def test_get_api(self):
        """Test that the API can be retrieved."""
        api_json = get_api()
        self.assertIn("/api", api_json)
        self.assertNotIn(self.login_v2, api_json)
        self.assertIn(self.login_v3, api_json)
        self.assertNotIn(self.logout_v2, api_json)
        self.assertIn(self.logout_v3, api_json)

    def test_get_api_by_version(self):
        """Test that the API can be filtered by version."""
        api_json = get_api("v3")
        self.assertNotIn(self.login_v2, api_json)
        self.assertIn(self.login_v3, api_json)

    def test_get_api_by_fragment(self):
        """Test that the API can be filtered by version and a fragment."""
        api_json = get_api("v3", "logout")
        self.assertNotIn(self.login_v3, api_json)
        self.assertIn(self.logout_v3, api_json)
