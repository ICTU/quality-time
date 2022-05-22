"""Test the reports collection."""

import unittest
from unittest.mock import Mock

from shared.model.report import Report

from database.reports import latest_report_for_uuids, metrics_of_subject

from ..fixtures import (
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


class MetricsForSubjectTest(unittest.TestCase):
    """Unittest for getting all metrics belonging to a single subject."""

    def setUp(self):
        """Override to create a mock database fixture."""
        self.database = Mock()
        self.database.reports.find_one.return_value = {
            "subjects": {SUBJECT_ID: {"metrics": {METRIC_ID: {}, METRIC_ID2: {}}}}
        }

    def test_metrics_of_subject(self):
        """Test if we get all metric id's in the subject."""
        metric_uuids = metrics_of_subject(self.database, SUBJECT_ID)

        self.assertEqual(len(metric_uuids), 2)
        for m_id in metric_uuids:
            self.assertIn(m_id, [METRIC_ID, METRIC_ID2])


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
        return super().setUp()

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
