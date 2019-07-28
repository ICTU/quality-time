"""Unit tests for the util module."""

import unittest

from datetime import datetime, timezone
from unittest.mock import patch
from utilities.functions import iso_timestamp, report_date_time, uuid


class UtilTests(unittest.TestCase):
    """Unit tests for the util methods."""

    def test_iso_timestamp(self):
        """Test that the iso timestamp has the correct format."""
        now = datetime(2019, 3, 3, 10, 4, 5, 567, tzinfo=timezone.utc)
        with patch("utilities.functions.datetime") as date_time:
            date_time.now.return_value = now
            self.assertEqual("2019-03-03T10:04:05+00:00", iso_timestamp())

    def test_report_date_time(self):
        """Test that the report datetime can be parsed from the HTTP request."""
        with patch("utilities.functions.bottle.request") as request:
            request.query = dict(report_date="2019-03-03T10:04:05Z")
            self.assertEqual("2019-03-03T10:04:05+00:00", report_date_time())

    def test_missing_report_date_time(self):
        """Test that the report datetime is now if it's not present in the request."""
        now = datetime(2019, 3, 3, 10, 4, 5, 567, tzinfo=timezone.utc)
        with patch("utilities.functions.bottle.request") as request:
            request.query = dict()
            with patch("utilities.functions.datetime") as date_time:
                date_time.now.return_value = now
                self.assertEqual("2019-03-03T10:04:05+00:00", report_date_time())

    def test_uuid(self):
        """Test the expected length of the uuid."""
        self.assertEqual(36, len(uuid()))
