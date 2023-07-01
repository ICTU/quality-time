"""Unit tests for the date time functions."""

import unittest
from datetime import datetime, timedelta

from dateutil.tz import tzlocal

from shared.utils.date_time import now


class NowTest(unittest.TestCase):
    """Unit tests for the now function."""

    def test_tz(self):
        """Test that the timezone of now is equal to the local timezone."""
        self.assertEqual(tzlocal(), now().tzinfo)

    def test_now_equals_datetime_now(self):
        """Test that now is equal to datetime.now() with the local timezone."""
        self.assertTrue(now() - datetime.now(tz=tzlocal()) < timedelta(seconds=1))
