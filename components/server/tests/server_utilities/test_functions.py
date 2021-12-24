"""Unit tests for the util module."""

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from server_utilities.functions import iso_timestamp, uuid


class UtilTests(unittest.TestCase):
    """Unit tests for the utility methods."""

    def test_iso_timestamp(self):
        """Test that the iso timestamp has the correct format."""
        expected_time_stamp = "2020-03-03T10:04:05+00:00"
        with patch("server_utilities.functions.datetime") as date_time:
            date_time.now.return_value = datetime(2020, 3, 3, 10, 4, 5, 567, tzinfo=timezone.utc)
            self.assertEqual(expected_time_stamp, iso_timestamp())

    def test_uuid(self):
        """Test the expected length of the uuid."""
        self.assertEqual(36, len(uuid()))
