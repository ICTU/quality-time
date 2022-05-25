"""Unit tests for the logos."""

import unittest

from shared.data_model.logos import LOGOS_ROOT


class LogosTest(unittest.TestCase):
    """Logos unit tests."""

    def test_path(self):
        """Test that the logos root is correct."""
        self.assertTrue(str(LOGOS_ROOT).endswith("logos"))
