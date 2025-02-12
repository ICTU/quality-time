"""Unit tests for the reports routes."""

import unittest

from routes import get_api_docs

EXTERNAL_API_VERSION = "v3"


class DocumentationTest(unittest.TestCase):
    """Unit tests for the documentation routes."""

    login_internal = "/api/internal/login"
    login_external = f"/api/{EXTERNAL_API_VERSION}/login"
    server_external = f"/api/{EXTERNAL_API_VERSION}/server"

    def test_get_api(self):
        """Test that the API can be retrieved."""
        api_json = get_api_docs()
        self.assertIn(self.login_internal, api_json)
        self.assertIn(self.login_external, api_json)
        self.assertIn(self.server_external, api_json)
