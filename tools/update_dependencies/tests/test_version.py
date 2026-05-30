"""Unit tests for the version module."""

import unittest

from version import is_valid


class IsValidTest(unittest.TestCase):
    """Unit tests for the is_valid version checker."""

    def test_is_valid(self):
        """Test that a valid version is reported as valid."""
        self.assertTrue(is_valid("1.0"))

    def test_is_invalid(self):
        """Test that a invalid version is reported as invalid."""
        self.assertFalse(is_valid("nope-1.0"))

    def test_v_prefix_is_allowed(self):
        """Test that a version with a v-prefix is valid."""
        self.assertTrue(is_valid("v1.0"))
