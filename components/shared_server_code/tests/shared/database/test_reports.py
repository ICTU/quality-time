"""Unit tests for the reports collection."""

import unittest
from unittest.mock import Mock

from shared.database.reports import insert_new_report

from tests.fixtures import JOHN, REPORT_ID, REPORT_ID2


class ReportsTest(unittest.TestCase):
    """Unit tests for the reports collection."""

    def setUp(self):
        """Override to setup the database."""
        self.database = Mock()
        self.database.sessions.find_one.return_value = JOHN

    def test_insert_one_report(self):
        """Test that a report can be inserted into the reports collection."""
        report = {"report_uuid": REPORT_ID}
        self.assertEqual({"ok": True}, insert_new_report(self.database, "delta", [REPORT_ID], report))

    def test_insert_multiple_reports(self):
        """Test that multiple reports can be inserted into the reports collection."""
        reports = [{"report_uuid": REPORT_ID}, {"report_uuid": REPORT_ID2, "_id": "id"}]
        self.assertEqual({"ok": True}, insert_new_report(self.database, "delta", [REPORT_ID], *reports))
