"""Unit tests for the logos."""

import pathlib
import unittest

from shared_data_model import logos
from shared_data_model.logos import get_logo


class LogosTest(unittest.TestCase):
    """Unit tests for the logos."""

    def test_get_logo(self):
        """Test that a logo canp be retrieved."""
        calendar_logo = pathlib.Path(logos.__file__).parent / "calendar.png"
        self.assertEqual(calendar_logo.read_bytes(), get_logo("calendar"))
