"""Unit tests for the utils module."""

import unittest
from datetime import datetime
from unittest.mock import patch

from dateutil.tz import tzutc

from shared.utils.functions import first, iso_timestamp, md5_hash, slugify


class IsoTimestampTest(unittest.TestCase):
    """Unit tests for the iso_timestamp function."""

    def test_iso_timestamp(self):
        """Test that the iso timestamp has the correct format."""
        expected_time_stamp = "2020-03-03T10:04:05+00:00"
        with patch("shared.utils.functions.datetime") as date_time:
            date_time.now.return_value = datetime(2020, 3, 3, 10, 4, 5, 567, tzinfo=tzutc())
            self.assertEqual(expected_time_stamp, iso_timestamp())


class FirstTest(unittest.TestCase):
    """Unit tests for the first function."""

    def test_first(self):
        """Test that the first item is returned."""
        self.assertEqual("first", first(["first", "second"]))

    def test_first_with_filter(self):
        """Test that the first item that matches the filter is returned."""
        self.assertEqual("second", first(["first", "second"], lambda item: item.startswith("s")))

    def test_empty_sequence(self):
        """Test that StopIteration is thrown when the sequence is empty."""
        self.assertRaises(StopIteration, first, [])


class MD5HashTest(unittest.TestCase):
    """Unit tests for the md5_hash function."""

    def test_hash(self):
        """Test that the md5 hash is returned."""
        self.assertEqual("acbd18db4cc2f85cedef654fccc4a4d8", md5_hash("foo"))


class SlugifyTest(unittest.TestCase):
    """Unit tests for the slugify function."""

    def test_simple_string(self):
        """Test that a simple string is returned unchanged."""
        self.assertEqual("#name", slugify("name"))

    def test_mixed_case(self):
        """Test that a upper case characters are made lower case."""
        self.assertEqual("#name", slugify("Name"))

    def test_forbidden_characters(self):
        """Test that forbidden characters are removed."""
        self.assertEqual("#name-part-two", slugify("/name part two()"))
