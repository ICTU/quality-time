"""Test the reports collection."""

import unittest
from unittest.mock import Mock

from shared.model.report import Report

from shared.database.reports import insert_new_report

from ...fixtures import REPORT_ID, REPORT_ID2, SUBJECT_ID


class InsertNewReportTest(unittest.TestCase):
    """Unittest for inserting one or more reports."""

    def setUp(self) -> None:
        """Override to create a mock database fixture."""
        self.database = Mock()
        self.database.sessions.find_one.return_value = {}
        return super().setUp()

    def test_insert_one(self):
        """Test that one report gets inserted."""
        report_to_insert = Report(
            {},
            {"title": "test", "subjects": {SUBJECT_ID: {}}, "report_uuid": REPORT_ID},
        )
        insert_new_report(
            self.database, "insert a test report", REPORT_ID, report_to_insert
        )

        self.database.reports.insert_one.assert_called_once_with(report_to_insert)

    def test_insert_many(self):
        """Test that multiple reports get inserted."""
        report_1 = Report(
            {},
            {"title": "test", "subjects": {SUBJECT_ID: {}}, "report_uuid": REPORT_ID},
        )
        report_2 = Report(
            {},
            {"title": "test2", "subjects": {SUBJECT_ID: {}}, "report_uuid": REPORT_ID2},
        )

        insert_new_report(
            self.database,
            "insert a test report",
            [REPORT_ID, REPORT_ID2],
            report_1,
            report_2,
        )

        self.database.reports.insert_many.assert_called_once_with(
            (report_1, report_2), ordered=False
        )

    def test__id_gets_removed(self):
        """Test that one report gets inserted."""
        report_to_insert = Report(
            {},
            {
                "_id": "testId",
                "title": "test",
                "subjects": {SUBJECT_ID: {}},
                "report_uuid": REPORT_ID,
            },
        )
        insert_new_report(
            self.database, "insert a test report", REPORT_ID, report_to_insert
        )

        self.database.reports.insert_one.assert_called_once_with(report_to_insert)
