"""Unit tests for the logo route."""

import unittest
from unittest.mock import patch

from external.routes import get_logo


class LogoTest(unittest.TestCase):
    """Unit tests for the logo route."""

    @patch("bottle.static_file")
    def test_logo(self, mock_static_file):
        """Test that a logo can be retrieved."""
        mock_static_file.return_value = "logo"
        self.assertEqual("logo", get_logo("sonarqube"))
