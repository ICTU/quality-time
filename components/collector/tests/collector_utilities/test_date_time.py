"""Unit tests for the date time functions."""

import unittest
from datetime import datetime, timedelta

from dateutil.tz import tzlocal, tzutc

from shared.utils.date_time import now

from collector_utilities.date_time import (
    datetime_from_parts,
    datetime_from_timestamp,
    days_ago,
    days_to_go,
    minutes,
    parse_datetime,
    parse_duration,
)


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
        self.assertEqual(datetime(2023, 5, 25, 23, 24, 0, tzinfo=tzlocal()), datetime_from_parts(2023, 5, 25, 23, 24))

    def test_datetime_without_time(self):
        """Test that the time can be left out."""
        self.assertEqual(datetime(2023, 5, 25, 0, 0, 0, tzinfo=tzlocal()), datetime_from_parts(2023, 5, 25))


class DateTimeFromTimestampTest(unittest.TestCase):
    """Unit tests for the datetime from timestamp function."""

    def test_timezone(self):
        """Test that the datetime has the local timezone."""
        self.assertEqual(tzlocal(), datetime_from_timestamp(1_000_000_000).tzinfo)


class MinutesTest(unittest.TestCase):
    """Unit tests for the minutes function."""

    def test_zero_minutes(self):
        """Test that an empty timedelta is zero minutes."""
        self.assertEqual(0, minutes(timedelta()))

    def test_round_down(self):
        """Test that 29 seconds is zero minutes."""
        self.assertEqual(0, minutes(timedelta(seconds=29)))

    def test_round_up(self):
        """Test that 31 seconds is one minute."""
        self.assertEqual(1, minutes(timedelta(seconds=31)))

    def test_hours(self):
        """Test that 2 hours seconds is 120 minutes."""
        self.assertEqual(120, minutes(timedelta(hours=2)))

    def test_days(self):
        """Test multiple days."""
        self.assertEqual(2 * 24 * 60, minutes(timedelta(days=2)))


class ParseDurationTest(unittest.TestCase):
    """Unit tests for the parse_duration function."""

    def test_empty_string(self):
        """Test that parsing the empty string results in a duration of 0 minutes."""
        self.assertEqual(0, parse_duration(""))

    def test_zero_seconds(self):
        """Test that parsing zero seconds results in a duration of 0 minutes."""
        self.assertEqual(0, parse_duration("0s"))

    def test_thirty_seconds(self):
        """Test that parsing thirty seconds results in a duration of 1 minute."""
        self.assertEqual(1, parse_duration("30s"))

    def test_zero_minutes(self):
        """Test that parsing zero minutes results in a duration of 0 minutes."""
        self.assertEqual(0, parse_duration("0m"))

    def test_zero_hours(self):
        """Test that parsing zero hours results in a duration of 0 minutes."""
        self.assertEqual(0, parse_duration("0h"))

    def test_ten_minutes(self):
        """Test that parsing ten minutes results in a duration of 10 minutes."""
        self.assertEqual(10, parse_duration("10m"))

    def test_hours_and_seconds(self):
        """Test that the minutes group can be missing."""
        self.assertEqual(121, parse_duration("2h 50s"))

    def test_hours_minutes_and_seconds(self):
        """Test all groups present."""
        self.assertEqual(124, parse_duration("2h 3m 50s"))

    def test_wrong_order(self):
        """Test all groups present."""
        self.assertEqual(0, parse_duration("2m 3h 50s"))

    def test_spaces_optional(self):
        """Test that spaces between groups are optional."""
        self.assertEqual(124, parse_duration("2h3m50s"))

    def test_whitespace_is_stripped(self):
        """Test that whitespace is stripped."""
        self.assertEqual(124, parse_duration("   2h3m     50s\t\t"))

    def test_no_match(self):
        """Test without match the result is 0."""
        self.assertEqual(0, parse_duration("2x3y50s"))

    def test_accept_invalid_number_of_seconds(self):
        """Test that an invalid number of seconds is accepted."""
        self.assertEqual(2, parse_duration("1m70s"))

    def test_accept_invalid_number_of_minutes(self):
        """Test that an invalid number of minutes is accepted."""
        self.assertEqual(360, parse_duration("1h300m"))
