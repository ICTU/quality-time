"""API tests."""

import unittest

import requests

from .base import WWW_URL


class ApiTest(unittest.TestCase):
    """Tests for the server API."""

    def test_documentation(self):
        """Test that the documentation API is available."""
        apis = requests.get(f"{WWW_URL}/api/v3/docs", timeout=10).json().keys()
        self.assertIn("/api/internal/login", apis)
        self.assertIn("/api/v3/login", apis)
