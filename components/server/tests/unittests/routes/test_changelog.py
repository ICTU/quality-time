"""Unit tests for the changelog routes."""

import unittest
from unittest.mock import Mock

from routes.changelog import get_changelog


class ChangeLogTest(unittest.TestCase):
    """Unit tests for getting the changelog."""

    def setUp(self):
        self.database = Mock()
        self.database.sessions.find_one.return_value = dict(user="Jenny")

    def test_get_changelog(self):
        """Test that the changelog is returned."""
        report1 = dict(timestamp="1", delta="delta1")
        report2 = dict(timestamp="2", delta="delta2")
        self.database.reports.find.return_value = [report2, report1]
        self.database.measurements.find.return_value = []
        self.assertEqual(dict(changelog=[report2, report1]), get_changelog("report_uuid", "10", self.database))

    def test_get_changelog_with_measurements(self):
        """Test that the changelog is returned."""
        report1 = dict(timestamp="1", delta="delta1")
        measurement2 = dict(delta="delta2", start="2")
        report3 = dict(timestamp="3", delta="delta3")
        self.database.reports.find.return_value = [report3, report1]
        self.database.measurements.find.return_value = [measurement2]
        self.assertEqual(
            dict(changelog=[report3, dict(delta="delta2", timestamp="2"), report1]),
            get_changelog("report_uuid", "10", self.database))
