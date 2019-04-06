"""Unit tests for the utility functions."""

import unittest

from src import util


class StableTracebackTest(unittest.TestCase):
    """Unit tests for the stable traceback function."""

    def test_no_memory_address(self):
        """Test that tracebacks without memory address are unchanged."""
        self.assertEqual("string", util.stable_traceback("string"))

    def test_memory_address(self):
        """Test that tracebacks without memory address are unchanged."""
        traceback = "NewConnectionError: <HTTPConnection object at 0x1087ea358>: Failed to establish a new connection"
        expected_tb = "NewConnectionError: <HTTPConnection object>: Failed to establish a new connection"
        self.assertEqual(expected_tb, util.stable_traceback(traceback))
