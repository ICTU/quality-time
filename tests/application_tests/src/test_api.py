"""API tests."""

import unittest

import requests


class ApiTest(unittest.TestCase):
    """Tests for the server API."""

    def test_documentation(self):
        """Test that the documentation API is available."""
        apis = requests.get("http://www:8080/api", timeout=10).json().keys()
        self.assertIn("/api/internal/login", apis)
        self.assertIn("/api/v3/login", apis)
