"""Unit tests for the utility functions."""

from datetime import datetime, timedelta, timezone
import unittest

from src.utilities.functions import days_ago, stable_traceback


class StableTracebackTest(unittest.TestCase):
    """Unit tests for the stable traceback function."""

    def test_no_memory_address(self):
        """Test that tracebacks without memory address are unchanged."""
        self.assertEqual("string", stable_traceback("string"))

    def test_memory_address(self):
        """Test that tracebacks without memory address are unchanged."""
        traceback = "NewConnectionError: <HTTPConnection object at 0x1087ea358>: Failed to establish a new connection"
        expected_tb = "NewConnectionError: <HTTPConnection object>: Failed to establish a new connection"
        self.assertEqual(expected_tb, stable_traceback(traceback))

    def test_no_tokens(self):
        """Test that tokens are redacted from tracebacks."""
        self.assertEqual(
            "http://example.com?id=5&token=<redacted>&page=0",
            stable_traceback("http://example.com?id=5&token=abcdef45321a&page=0"))

    def test_no_keys(self):
        """Test that keys are redacted from tracebacks."""
        self.assertEqual(
            "http://example.com?key=<redacted>&id=5", stable_traceback("http://example.com?key=abcdef45321a&id=5"))


class DaysAgoTest(unittest.TestCase):
    """Unit tests for the days ago method."""

    def test_days_ago(self):
        """Test that the days ago works properly with timezones."""
        self.assertEqual(0, days_ago(datetime.now() - timedelta(hours=23)))
        self.assertEqual(1, days_ago(datetime.now() - timedelta(hours=24)))
        self.assertEqual(1, days_ago(datetime.now(tz=timezone.utc) - timedelta(hours=47)))
        self.assertEqual(2, days_ago(datetime.now(tz=timezone.utc) - timedelta(hours=48)))
