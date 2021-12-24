"""Unit tests for the utils module."""

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from external.utils.functions import report_date_time


@patch("server_utilities.functions.bottle.request")
class ReportDateTimeTest(unittest.TestCase):
    """Unit tests for the report_datetime method."""

    def setUp(self):
        """Override to setup the 'current' time."""
        self.now = datetime(2019, 3, 3, 10, 4, 5, 567, tzinfo=timezone.utc)
        self.expected_time_stamp = "2019-03-03T10:04:05+00:00"

    def test_report_date_time(self, request):
        """Test that the report datetime can be parsed from the HTTP request."""
        request.query = dict(report_date="2019-03-03T10:04:05Z")
        self.assertEqual(self.expected_time_stamp, report_date_time())

    def test_missing_report_date_time(self, request):
        """Test that the report datetime is empty if it's not present in the request."""
        request.query = {}
        self.assertEqual("", report_date_time())

    def test_future_report_date_time(self, request):
        """Test that the report datetime is empty if it's a future date."""
        request.query = dict(report_date="3000-01-01T00:00:00Z")
        self.assertEqual("", report_date_time())
