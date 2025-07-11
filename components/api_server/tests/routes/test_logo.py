"""Unit tests for the logo route."""

import unittest
from unittest.mock import Mock, patch

import bottle

from routes import get_logo


class LogoTest(unittest.TestCase):
    """Unit tests for the logo route."""

    @patch("importlib.resources.read_binary", Mock(return_value="logo"))
    def test_logo(self):
        """Test that a logo can be retrieved."""
        self.assertEqual("logo", get_logo("sonarqube"))
        self.assertEqual("image/png", bottle.response.get_header("Content-Type"))

    def test_missing_logo(self):
        """Test that retrieving a missing logo results in a 404."""
        self.assertRaises(bottle.HTTPError, get_logo, "missing")
