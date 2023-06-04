"""Unit tests for the date time functions."""

import unittest
from datetime import datetime, timedelta

from dateutil.tz import tzlocal, tzutc

from collector_utilities.date_time import (
    datetime_fromparts,
    datetime_fromtimestamp,
    days_ago,
    days_to_go,
    now,
    parse_datetime,
)


class NowTest(unittest.TestCase):
    """Unit tests for the now function."""

    def test_tz(self):
        """Test that the timezone of now is equal to the local timezone."""
        self.assertEqual(tzlocal(), now().tzinfo)

    def test_now_equals_datetime_now(self):
        """Test that now is equal to datetime.now() with the local timezone."""
        self.assertTrue(now() - datetime.now(tz=tzlocal()) < timedelta(seconds=1))


class DaysAgoTest(unittest.TestCase):
    """Unit tests for the days_ago function."""

    def test_now(self):
        """Test that now is zero days ago."""
        self.assertEqual(0, days_ago(now()))

    def test_one_hour_ago(self):
        """Test that an hour is zero days ago."""
        self.assertEqual(0, days_ago(now() - timedelta(hours=1)))

    def test_yesterday(self):
        """Test that yesterday is one day ago."""
        self.assertEqual(1, days_ago(now() - timedelta(days=1)))

    def test_last_week(self):
        """Test that a week ago is seven days ago."""
        self.assertEqual(7, days_ago(now() - timedelta(weeks=1)))

    def test_tomorrow(self):
        """Test that tomorrow is zero days ago."""
        self.assertEqual(0, days_ago(now() + timedelta(days=1)))


class DaysToGoTest(unittest.TestCase):
    """Unit tests for the days_togo function."""

    def test_now(self):
        """Test that now is zero days to go."""
        self.assertEqual(0, days_to_go(now()))

    def test_one_hour_from_now(self):
        """Test that an hour is zero days ago."""
        self.assertEqual(0, days_ago(now() + timedelta(hours=1)))

    def test_tomorrow(self):
        """Test that tomorrow is one day to go."""
        self.assertEqual(1, days_to_go(now() + timedelta(days=1)))

    def test_next_week(self):
        """Test that next week is seven days to go."""
        self.assertEqual(7, days_to_go(now() + timedelta(weeks=1)))

    def test_yesterday(self):
        """Test that yesterday is zero days to go."""
        self.assertEqual(0, days_to_go(now() - timedelta(days=1)))


class ParseDateTimeTest(unittest.TestCase):
    """Unit tests for the parse_datetime function."""

    def test_datetime_without_timezone(self):
        """Test that a date time without timezone gets the local time zone."""
        self.assertEqual(tzlocal(), parse_datetime("2023-05-25T23:11:00").tzinfo)

    def test_datetime_with_timezone(self):
        """Test that a date time with timezone gets the parsed time zone."""
        self.assertEqual(tzutc(), parse_datetime("2023-05-25T23:11:00Z").tzinfo)


class DateTimeFromPartsTest(unittest.TestCase):
    """Unit tests for the datetime from parts function."""

    def test_datetime_with_time(self):
        """Test that the time can be passed."""
        self.assertEqual(datetime(2023, 5, 25, 23, 24, 0, tzinfo=tzlocal()), datetime_fromparts(2023, 5, 25, 23, 24))

    def test_datetime_without_time(self):
        """Test that the time can be left out."""
        self.assertEqual(datetime(2023, 5, 25, 0, 0, 0, tzinfo=tzlocal()), datetime_fromparts(2023, 5, 25))


class DateTimeFromTimestampTest(unittest.TestCase):
    """Unit tests for the datetime from timstamp function."""

    def test_timezone(self):
        """Test that the datetime has the local timezone."""
        self.assertEqual(tzlocal(), datetime_fromtimestamp(1000000).tzinfo)
