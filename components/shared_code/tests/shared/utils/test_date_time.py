"""Unit tests for the date time functions."""

import unittest
from datetime import datetime, timedelta

from dateutil.tz import tzlocal, tzutc

from shared.utils.date_time import now, parse_datetime


class NowTest(unittest.TestCase):
    """Unit tests for the now function."""

    def test_tz(self):
        """Test that the timezone of now is equal to the local timezone."""
        self.assertEqual(tzlocal(), now().tzinfo)

    def test_now_equals_datetime_now(self):
        """Test that now is equal to datetime.now() with the local timezone."""
        self.assertLess(now() - datetime.now(tz=tzlocal()), timedelta(seconds=1))


class ParseDateTimeTest(unittest.TestCase):
    """Unit tests for the parse_datetime function."""

    def test_datetime_without_timezone(self):
        """Test that a date time without timezone gets the local time zone."""
        self.assertEqual(tzlocal(), parse_datetime("2023-05-25T23:11:00").tzinfo)

    def test_datetime_with_timezone(self):
        """Test that a date time with timezone gets the parsed time zone."""
        self.assertEqual(tzutc(), parse_datetime("2023-05-25T23:11:00Z").tzinfo)
