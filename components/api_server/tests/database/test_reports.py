"""Test the reports collection."""

import unittest
from unittest.mock import Mock

from shared.model.report import Report

from database.reports import insert_new_report, latest_report_for_uuids

from tests.fixtures import (
    JOHN,
    METRIC_ID,
    METRIC_ID2,
    METRIC_ID3,
    METRIC_ID4,
    REPORT_ID,
    REPORT_ID2,
    SOURCE_ID,
    SOURCE_ID2,
    SUBJECT_ID,
    SUBJECT_ID2,
)


class LatestReportForUuidsTest(unittest.TestCase):
    """Unittest for getting specific reports based on uuids."""

    def setUp(self) -> None:
        """Override to create a mock database fixture."""
        self.all_reports = [
            Report(
                {},
                {
                    "report_uuid": REPORT_ID,
                    "subjects": {SUBJECT_ID: {"metrics": {METRIC_ID: {"sources": {SOURCE_ID: {}}}, METRIC_ID2: {}}}},
                },
            ),
            Report(
                {},
                {"report_uuid": REPORT_ID2, "subjects": {SUBJECT_ID2: {"metrics": {METRIC_ID3: {}, METRIC_ID4: {}}}}},
            ),
        ]

    def test_existing_uuids(self):
        """Test that function works for report, subject, metric and source uuids."""
        reports = latest_report_for_uuids(self.all_reports, REPORT_ID)
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0].uuid, REPORT_ID)

        reports = latest_report_for_uuids(self.all_reports, SUBJECT_ID2)
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0].uuid, REPORT_ID2)

        reports = latest_report_for_uuids(self.all_reports, METRIC_ID3)
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0].uuid, REPORT_ID2)

        reports = latest_report_for_uuids(self.all_reports, SOURCE_ID)
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0].uuid, REPORT_ID)

    def test_multiple_uuids(self):
        """Test that function works for report, subject, metric and source uuids."""
        reports = latest_report_for_uuids(self.all_reports, SUBJECT_ID2, REPORT_ID)
        self.assertEqual(len(reports), 2)
        self.assertEqual(reports[0].uuid, REPORT_ID2)
        self.assertEqual(reports[1].uuid, REPORT_ID)

    def test_non_existing_uuid(self):
        """Test that function works for report, subject, metric and source uuids."""
        reports = latest_report_for_uuids(self.all_reports, SOURCE_ID2)
        self.assertEqual(len(reports), 0)


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
