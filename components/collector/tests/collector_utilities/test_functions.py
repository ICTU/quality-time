"""Unit tests for the utility functions."""

import unittest
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from collector_utilities.date_time import days_ago
from collector_utilities.functions import (
    add_query,
    decimal_round_half_up,
    hashless,
    is_regexp,
    iterable_to_batches,
    stable_traceback,
    tokenless,
)
from collector_utilities.type import URL


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
            "https://example.com?id=5&token=<redacted>&page=0",
            stable_traceback("https://example.com?id=5&token=abcdef_45321-a&page=0"),
        )

    def test_no_keys(self):
        """Test that keys are redacted from tracebacks."""
        self.assertEqual(
            "https://example.com?key=<redacted>&id=5",
            stable_traceback("https://example.com?key=abcdef45321a&id=5"),
        )


class SafeURLTest(unittest.TestCase):
    """Unit tests for the safe for logging function."""

    def test_no_token(self):
        """Test that the URL is returned unchanged if it does not contain a token."""
        url = URL("https://url/path/1")
        self.assertEqual(url, tokenless(url))

    def test_private_token(self):
        """Test that the URL is returned without the private token."""
        self.assertEqual(
            URL("https://url/path?private_token=<redacted>"),
            tokenless(URL("https://url/path?private_token=abcdef45321a")),
        )


class DaysAgoTest(unittest.TestCase):
    """Unit tests for the days ago function."""

    def test_days_ago(self):
        """Test that the days ago works properly with timezones."""
        self.assertEqual(0, days_ago(datetime.now(tz=UTC) - timedelta(hours=23)))
        self.assertEqual(1, days_ago(datetime.now(tz=UTC) - timedelta(hours=24)))
        self.assertEqual(1, days_ago(datetime.now(tz=UTC) - timedelta(hours=47)))
        self.assertEqual(2, days_ago(datetime.now(tz=UTC) - timedelta(hours=48)))


class StripHashTest(unittest.TestCase):
    """Unit tests for the strip hash function."""

    def test_no_hash(self):
        """Test that an url without hash is returned unchanged."""
        expected_url = url = URL("https://www.google.com/")
        self.assertEqual(expected_url, hashless(url))

    def test_hash(self):
        """Test that an url with hash is returned without the hash."""
        url = URL("https://test1.app.example.org:1234/main.58064cb8d36474bd79f9.js")
        expected_url = URL("https://test1.app.example.org:1234/main.hashremoved.js")
        self.assertEqual(expected_url, hashless(url))

    def test_uppercase_hash(self):
        """Test that an url with uppercase hash is returned without the hash."""
        url = URL("https://test2.app.example.org:1234/main.58064CB8D36474BD79F9.js")
        expected_url = URL("https://test2.app.example.org:1234/main.hashremoved.js")
        self.assertEqual(expected_url, hashless(url))

    def test_long_hash(self):
        """Test that an url with a long hash is returned without the hash."""
        url = URL("https://test3.app.example.org:1234/main.58064cb8d36474bd79f956dc4ac40404d.js")
        expected_url = URL("https://test3.app.example.org:1234/main.hashremoved.js")
        self.assertEqual(expected_url, hashless(url))

    def test_hash_in_host(self):
        """Test that an url with a host name that matches the hash regular expression is returned unchanged."""
        expected_url = url = URL("https://test.app58064cb8d36474bd79f9.example.org:1234/main.js")
        self.assertEqual(expected_url, hashless(url))


class AddQueryTest(unittest.TestCase):
    """Unit tests for the add_query funcion."""

    def setUp(self):
        """Set up test fixtures."""
        self.url = URL("https://example.org")

    def test_add_query_to_url_without_query(self):
        """Test adding a query to a URL without queries."""
        self.assertEqual(self.url, add_query(self.url, ""))
        self.assertEqual(URL("https://example.org?a=b"), add_query(self.url, "a=b"))
        self.assertEqual(URL("https://example.org?a=b&c=d"), add_query(self.url, "a=b&c=d"))

    def test_add_query_to_url_with_query(self):
        """Test adding a query to a URL with queries."""
        url = add_query(self.url, "a=b")
        self.assertEqual(url, add_query(url, ""))
        self.assertEqual(URL("https://example.org?a=b&c=d"), add_query(url, "c=d"))
        self.assertEqual(URL("https://example.org?a=b&c=d&e=f"), add_query(url, "c=d&e=f"))


class IsRegularExpressionTest(unittest.TestCase):
    """Unit tests for the is_regexp function."""

    def test_is_regexp(self):
        """Test that regular expressions are recognized."""
        self.assertFalse(is_regexp(""))
        self.assertFalse(is_regexp("No punctuation"))
        self.assertTrue(is_regexp(".*"))
        self.assertTrue(is_regexp("bar?foo"))
        self.assertTrue(is_regexp("[a-z]+foo"))

    def test_semantic_version_are_no_regexp(self):
        """Test that semantic version numbers are not considered a regular expression."""
        self.assertFalse(is_regexp("1.2.3"))
        self.assertFalse(is_regexp("1.2.3-rc.0"))
        self.assertTrue(is_regexp("v10.2"))
        self.assertTrue(is_regexp("foo 10.2"))


class IterableToBatchesTest(unittest.TestCase):
    """Unit tests for the iterable_to_batches function."""

    def test_iterable_to_batches(self):
        """Test that iterable is split in batches."""
        self.assertEqual([(0, 1, 2)], list(iterable_to_batches(range(3), 5)))
        self.assertEqual([(0, 1, 2), (3, 4, 5), (6,)], list(iterable_to_batches(range(7), 3)))


class DecimalRoundHalfUpTest(unittest.TestCase):
    """Unit tests for the decimal_round_half_up function."""

    def test_decimal_round_half_up(self):
        """Test that decimal inputs are rounded according to the ROUND_HALF_UP mode."""
        self.assertEqual(1, decimal_round_half_up(1.0))
        self.assertEqual(1, decimal_round_half_up(1.1))
        self.assertEqual(2, decimal_round_half_up(1.5))
        self.assertEqual(2, decimal_round_half_up(Decimal("1.5")))
