"""Unit tests for the reports routes."""

import unittest

from routes import get_api

EXTERNAL_API_VERSION = "v3"


class DocumentationTest(unittest.TestCase):
    """Unit tests for the documentation routes."""

    reports_overview_internal = "/api/internal/reports_overview/pdf"
    reports_overview_external = f"/api/{EXTERNAL_API_VERSION}/reports_overview/pdf"
    server_external = f"/api/{EXTERNAL_API_VERSION}/server"

    def test_get_api(self):
        """Test that the API can be retrieved."""
        api_json = get_api()
        self.assertIn("/api", api_json)
        self.assertIn(self.reports_overview_internal, api_json)
        self.assertIn(self.reports_overview_external, api_json)
        self.assertIn(self.server_external, api_json)

    def test_get_api_by_version(self):
        """Test that the API can be filtered by version."""
        api_json = get_api(EXTERNAL_API_VERSION)
        self.assertNotIn(self.reports_overview_internal, api_json)
        self.assertIn(self.reports_overview_external, api_json)
        self.assertIn(self.server_external, api_json)

    def test_get_api_by_fragment(self):
        """Test that the API can be filtered by version and a fragment."""
        api_json = get_api(EXTERNAL_API_VERSION, "reports_overview/pdf")
        self.assertNotIn(self.reports_overview_internal, api_json)
        self.assertIn(self.reports_overview_external, api_json)
        self.assertNotIn(self.server_external, api_json)
