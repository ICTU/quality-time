"""Unit tests for the util module."""

import unittest

from datetime import datetime, timezone
from unittest.mock import patch
from utilities.functions import iso_timestamp


class UtilTests(unittest.TestCase):
    """Unit tests for the util methods."""

    def test_iso_timestamp(self):
        """Test that the iso timestamp has the correct format."""
        now = datetime(2019, 3, 3, 10, 4, 5, 567, tzinfo=timezone.utc)
        with patch("utilities.functions.datetime") as date_time:
            date_time.now.return_value = now
            self.assertEqual("2019-03-03T10:04:05+00:00", iso_timestamp())
