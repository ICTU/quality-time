"""Unit tests for the util module."""

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from shared.utils.functions import iso_timestamp, md5_hash, report_date_time


class UtilTests(unittest.TestCase):
    """Unit tests for the utility methods."""

    def test_iso_timestamp(self):
        """Test that the iso timestamp has the correct format."""
        expected_time_stamp = "2020-03-03T10:04:05+00:00"
        with patch("shared.utils.functions.datetime") as date_time:
            date_time.now.return_value = datetime(
                2020, 3, 3, 10, 4, 5, 567, tzinfo=timezone.utc
            )
            self.assertEqual(expected_time_stamp, iso_timestamp())


class ReportDateTimeTest(unittest.TestCase):
    """Unit tests for the report_datetime method."""

    def setUp(self):
        """Override to setup the 'current' time."""
        self.now = datetime(2019, 3, 3, 10, 4, 5, 567, tzinfo=timezone.utc)
        self.expected_time_stamp = "2019-03-03T10:04:05+00:00"

    def test_report_date_time(self):
        """Test that the report datetime can be parsed from the HTTP request."""
        self.assertEqual(
            self.expected_time_stamp, report_date_time("2019-03-03T10:04:05Z")
        )

    def test_missing_report_date_time(self):
        """Test that the report datetime is empty if it's not present in the request."""
        self.assertEqual("", report_date_time("3000-01-01T00:00:00Z"))

    def test_future_report_date_time(self):
        """Test that the report datetime is empty if it's a future date."""
        self.assertEqual("", report_date_time("3000-01-01T00:00:00Z"))

    def test_no_date_available(self):
        """Test that the report datetime is empty if there is no input date."""
        self.assertEqual("", report_date_time(""))


class MD5HashTest(unittest.TestCase):
    """Unittest for md5 hash function."""

    def test_hash(self):
        """Test that the hash is correct."""
        string = "test"
        string_hash = md5_hash(string)
        self.assertEqual(string_hash, "098f6bcd4621d373cade4e832627b4f6")
