"""Unit tests for the subject routes."""

import unittest
from unittest.mock import Mock, patch

from external.routes import (
    delete_subject,
    get_subject_measurements,
    post_move_subject,
    post_new_subject,
    post_subject_attribute,
    post_subject_copy,
)
from shared.model.report import Report
from shared.utils.type import SubjectId

from ...fixtures import METRIC_ID, REPORT_ID, REPORT_ID2, SUBJECT_ID, SUBJECT_ID2, create_report


class GetSubjectTest(unittest.TestCase):
    """Unit tests for the get subject measurements endpoint."""

    def setUp(self):
        """Override to create a mock database fixture."""
        self.database = Mock()

    def test_get_subject_measurements(self):
        """Tests that the measurements for the requested metric are returned."""
        # Mock reports collection
        self.database.reports.find_one.return_value = {"subjects": {SUBJECT_ID: {"metrics": {METRIC_ID: {}}}}}
        # Mock measurements collection
        self.database.measurements.find_one.return_value = dict(start="1")
        self.database.measurements.find.return_value = [dict(start="0"), dict(start="1")]
        self.assertEqual(
            dict(measurements=[dict(start="0"), dict(start="1")]), get_subject_measurements(SUBJECT_ID, self.database)
        )


@patch("bottle.request")
class PostSubjectAttributeTest(unittest.TestCase):
    """Unit tests for the post subject report attribute route."""

    def setUp(self):
        """Override to create a mock database fixture."""
        self.database = Mock()
        self.report = Report(
            None,
            dict(
                _id="id",
                report_uuid=REPORT_ID,
                title="Report",
                subjects={SUBJECT_ID: dict(name="subject1"), SUBJECT_ID2: dict(type="subject_type")},
            ),
        )
        self.database.reports.find.return_value = [self.report]
        self.database.measurements.find.return_value = []
        self.database.datamodels.find_one.return_value = dict(
            _id="id", subjects=dict(subject_type=dict(name="subject2"))
        )
        self.email = "john@example.org"
        self.database.sessions.find_one.return_value = dict(user="John", email=self.email)

    def assert_delta(self, delta: str, subject_id: SubjectId, report: dict) -> None:
        """Check that the delta is correct."""
        self.assertEqual(
            dict(uuids=[REPORT_ID, subject_id], email=self.email, description=f"John changed the {delta}."),
            report["delta"],
        )

    def test_post_subject_name(self, request):
        """Test that the subject name can be changed."""
        request.json = dict(name="new name")
        self.assertEqual(dict(ok=True), post_subject_attribute(SUBJECT_ID, "name", self.database))
        self.database.reports.insert_one.assert_called_once_with(self.report)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            "name of subject 'subject1' in report 'Report' from 'subject1' to 'new name'", SUBJECT_ID, updated_report
        )

    def test_post_position_first(self, request):
        """Test that a subject can be moved to the top."""
        request.json = dict(position="first")
        self.assertEqual(dict(ok=True), post_subject_attribute(SUBJECT_ID2, "position", self.database))
        self.database.reports.insert_one.assert_called_once_with(self.report)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assertEqual([SUBJECT_ID2, SUBJECT_ID], list(updated_report["subjects"].keys()))
        self.assert_delta(
            "position of subject 'subject2' in report 'Report' from '1' to '0'", SUBJECT_ID2, updated_report
        )

    def test_post_position_last(self, request):
        """Test that a subject can be moved to the bottom."""
        request.json = dict(position="last")
        self.assertEqual(dict(ok=True), post_subject_attribute(SUBJECT_ID, "position", self.database))
        self.database.reports.insert_one.assert_called_once_with(self.report)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assertEqual([SUBJECT_ID2, SUBJECT_ID], list(updated_report["subjects"].keys()))
        self.assert_delta(
            "position of subject 'subject1' in report 'Report' from '0' to '1'", SUBJECT_ID, updated_report
        )

    def test_post_position_previous(self, request):
        """Test that a subject can be moved up."""
        request.json = dict(position="previous")
        self.assertEqual(dict(ok=True), post_subject_attribute(SUBJECT_ID2, "position", self.database))
        self.database.reports.insert_one.assert_called_once_with(self.report)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assertEqual([SUBJECT_ID2, SUBJECT_ID], list(updated_report["subjects"].keys()))
        self.assert_delta(
            "position of subject 'subject2' in report 'Report' from '1' to '0'", SUBJECT_ID2, updated_report
        )

    def test_post_position_next(self, request):
        """Test that a subject can be moved down."""
        request.json = dict(position="next")
        self.assertEqual(dict(ok=True), post_subject_attribute(SUBJECT_ID, "position", self.database))
        self.database.reports.insert_one.assert_called_once_with(self.report)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assertEqual([SUBJECT_ID2, SUBJECT_ID], list(updated_report["subjects"].keys()))
        self.assert_delta(
            "position of subject 'subject1' in report 'Report' from '0' to '1'", SUBJECT_ID, updated_report
        )

    def test_post_position_first_previous(self, request):
        """Test that moving the first subject up does nothing."""
        request.json = dict(position="previous")
        self.assertEqual(dict(ok=True), post_subject_attribute(SUBJECT_ID, "position", self.database))
        self.database.reports.insert_one.assert_not_called()

    def test_post_position_last_next(self, request):
        """Test that moving the last subject down does nothing."""
        request.json = dict(position="next")
        self.assertEqual(dict(ok=True), post_subject_attribute(SUBJECT_ID2, "position", self.database))
        self.database.reports.insert_one.assert_not_called()

    def test_post_unsafe_comment(self, request):
        """Test that comments are sanitized, since they are displayed as inner HTML in the frontend."""
        request.json = dict(comment='Comment with script<script type="text/javascript">alert("Danger")</script>')
        self.assertEqual(dict(ok=True), post_subject_attribute(SUBJECT_ID, "comment", self.database))
        self.database.reports.insert_one.assert_called_once_with(self.report)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            "comment of subject 'subject1' in report 'Report' from '' to 'Comment with script'",
            SUBJECT_ID,
            updated_report,
        )


class SubjectTest(unittest.TestCase):
    """Unit tests for adding and deleting subjects."""

    def setUp(self):
        """Override to create a mock database fixture."""
        self.database = Mock()
        self.email = "jenny@example.org"
        self.database.sessions.find_one.return_value = dict(user="Jenny", email=self.email)
        self.report = create_report()
        self.database.reports.find.return_value = [self.report]
        self.database.measurements.find.return_value = []
        self.database.datamodels.find_one.return_value = dict(
            _id="id",
            metrics=dict(metric_type=dict(name="Metric type")),
            subjects=dict(subject_type=dict(name="Subject", description="")),
            sources=dict(source_type=dict(name="Source type")),
        )

    def assert_delta(self, delta: str, uuids, report=None) -> None:
        """Check that the delta is correct."""
        report = report or self.report
        self.assertEqual(
            dict(uuids=sorted(uuids), email=self.email, description=f"Jenny {delta}."),
            report["delta"],
        )

    def test_add_subject(self):
        """Test that a subject can be added."""
        result = post_new_subject(REPORT_ID, self.database)
        self.assertTrue(result["ok"])
        self.assertIn("new_subject_uuid", result)
        subject_uuid = result["new_subject_uuid"]
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta("created a new subject in report 'Report'", [REPORT_ID, subject_uuid], report=updated_report)

    def test_copy_subject(self):
        """Test that a subject can be copied."""
        result = post_subject_copy(SUBJECT_ID, REPORT_ID, self.database)
        self.assertTrue(result["ok"])
        self.database.reports.insert_one.assert_called_once()
        updated_report = self.database.reports.insert_one.call_args[0][0]
        inserted_subjects = updated_report["subjects"]
        self.assertEqual(2, len(inserted_subjects))
        subject_copy_uuid = list(self.report["subjects"].keys())[1]
        self.assert_delta(
            "copied the subject 'Subject' from report 'Report' to report 'Report'",
            [REPORT_ID, subject_copy_uuid],
            report=updated_report,
        )

    def test_delete_subject(self):
        """Test that a subject can be deleted."""
        self.assertEqual(dict(ok=True), delete_subject(SUBJECT_ID, self.database))
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta("deleted the subject 'Subject' from report 'Report'", [REPORT_ID, SUBJECT_ID], updated_report)

    def test_move_subject(self):
        """Test that a subject can be moved to another report."""
        subject = self.report["subjects"][SUBJECT_ID]
        target_report = dict(_id="target_report", title="Target", report_uuid=REPORT_ID2, subjects={})
        self.database.reports.find.return_value = [self.report, target_report]
        self.assertEqual(dict(ok=True), post_move_subject(SUBJECT_ID, REPORT_ID2, self.database))
        self.assertEqual({}, self.report["subjects"])
        self.assertEqual((SUBJECT_ID, subject), next(iter(target_report["subjects"].items())))
        expected_description = "moved the subject 'Subject' from report 'Report' to report 'Target'"
        expected_uuids = [REPORT_ID, REPORT_ID2, SUBJECT_ID]

        updated_reports = self.database.reports.insert_many.call_args[0][0]
        for updated_report in updated_reports:
            self.assert_delta(expected_description, expected_uuids, updated_report)
