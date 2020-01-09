"""Unit tests for the subject routes."""

import unittest
from unittest.mock import Mock, patch

from routes.subject import (
    delete_subject, post_move_subject, post_new_subject, post_subject_attribute, post_subject_copy)

from .fixtures import REPORT_ID, REPORT_ID2, SUBJECT_ID, SUBJECT_ID2, create_report


@patch("bottle.request")
class PostSubjectAttributeTest(unittest.TestCase):
    """Unit tests for the post subject report attribute route."""

    def setUp(self):
        self.database = Mock()
        self.report = dict(
            _id="id", report_uuid=REPORT_ID, title="Report",
            subjects={SUBJECT_ID: dict(name="subject1"), SUBJECT_ID2: dict(name="subject2")})
        self.database.reports.find_one.return_value = self.report
        self.database.reports.distinct.return_value = [REPORT_ID]
        self.database.measurements.find.return_value = []
        self.database.datamodels.find_one.return_value = {}
        self.database.sessions.find_one.return_value = dict(user="John")

    def test_post_subject_name(self, request):
        """Test that the subject name can be changed."""
        request.json = dict(name="new name")
        self.assertEqual(dict(ok=True), post_subject_attribute(SUBJECT_ID, "name", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(uuids=[REPORT_ID, SUBJECT_ID],
                 description="John changed the name of subject 'subject1' in report 'Report' from 'subject1' to "
                             "'new name'."),
            self.report["delta"])

    def test_post_position_first(self, request):
        """Test that a subject can be moved to the top."""
        request.json = dict(position="first")
        self.assertEqual(dict(ok=True), post_subject_attribute(SUBJECT_ID2, "position", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual([SUBJECT_ID2, SUBJECT_ID], list(self.report["subjects"].keys()))
        self.assertEqual(
            dict(uuids=[REPORT_ID, SUBJECT_ID2],
                 description="John changed the position of subject 'subject2' in report 'Report' from '1' to '0'."),
            self.report["delta"])

    def test_post_position_last(self, request):
        """Test that a subject can be moved to the bottom."""
        request.json = dict(position="last")
        self.assertEqual(dict(ok=True), post_subject_attribute(SUBJECT_ID, "position", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual([SUBJECT_ID2, SUBJECT_ID], list(self.report["subjects"].keys()))
        self.assertEqual(
            dict(uuids=[REPORT_ID, SUBJECT_ID],
                 description="John changed the position of subject 'subject1' in report 'Report' from '0' to '1'."),
            self.report["delta"])

    def test_post_position_previous(self, request):
        """Test that a subject can be moved up."""
        request.json = dict(position="previous")
        self.assertEqual(dict(ok=True), post_subject_attribute(SUBJECT_ID2, "position", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual([SUBJECT_ID2, SUBJECT_ID], list(self.report["subjects"].keys()))
        self.assertEqual(
            dict(uuids=[REPORT_ID, SUBJECT_ID2],
                 description="John changed the position of subject 'subject2' in report 'Report' from '1' to '0'."),
            self.report["delta"])

    def test_post_position_next(self, request):
        """Test that a subject can be moved down."""
        request.json = dict(position="next")
        self.assertEqual(dict(ok=True), post_subject_attribute(SUBJECT_ID, "position", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual([SUBJECT_ID2, SUBJECT_ID], list(self.report["subjects"].keys()))
        self.assertEqual(
            dict(uuids=[REPORT_ID, SUBJECT_ID],
                 description="John changed the position of subject 'subject1' in report 'Report' from '0' to '1'."),
            self.report["delta"])

    def test_post_position_first_previous(self, request):
        """Test that moving the first subject up does nothing."""
        request.json = dict(position="previous")
        self.assertEqual(dict(ok=True), post_subject_attribute(SUBJECT_ID, "position", self.database))
        self.database.reports.insert.assert_not_called()
        self.assertEqual([SUBJECT_ID, SUBJECT_ID2], list(self.report["subjects"].keys()))

    def test_post_position_last_next(self, request):
        """Test that moving the last subject down does nothing."""
        request.json = dict(position="next")
        self.assertEqual(dict(ok=True), post_subject_attribute(SUBJECT_ID2, "position", self.database))
        self.database.reports.insert.assert_not_called()
        self.assertEqual([SUBJECT_ID, SUBJECT_ID2], list(self.report["subjects"].keys()))


class SubjectTest(unittest.TestCase):
    """Unit tests for adding and deleting subjects."""

    def setUp(self):
        self.database = Mock()
        self.database.sessions.find_one.return_value = dict(user="Jenny")
        self.database.reports.distinct.return_value = [REPORT_ID]
        self.database.reports.find_one.return_value = self.report = create_report()
        self.database.measurements.find.return_value = []
        self.database.datamodels.find_one.return_value = dict(
            _id="id",
            metrics=dict(metric_type=dict(name="Metric type")),
            subjects=dict(subject_type=dict(name="Subject", description="")),
            sources=dict(source_type=dict(name="Source type")))

    def test_add_subject(self):
        """Test that a subject can be added."""
        self.assertEqual(dict(ok=True), post_new_subject(REPORT_ID, self.database))
        subject_uuid = list(self.report["subjects"].keys())[1]
        self.assertEqual(
            dict(uuids=[REPORT_ID, subject_uuid], description="Jenny created a new subject in report 'Report'."),
            self.report["delta"])

    def test_copy_subject(self):
        """Test that a subject can be copied."""
        self.assertEqual(dict(ok=True), post_subject_copy(SUBJECT_ID, self.database))
        self.database.reports.insert.assert_called_once()
        inserted_subjects = self.database.reports.insert.call_args[0][0]["subjects"]
        self.assertEqual(2, len(inserted_subjects))
        subject_copy_uuid = list(self.report["subjects"].keys())[1]
        self.assertEqual(
            dict(uuids=[REPORT_ID, SUBJECT_ID, subject_copy_uuid],
                 description="Jenny copied the subject 'Subject' in report 'Report'."),
            self.report["delta"])

    def test_delete_subject(self):
        """Test that a subject can be deleted."""
        self.assertEqual(dict(ok=True), delete_subject(SUBJECT_ID, self.database))
        self.assertEqual(
            dict(uuids=[REPORT_ID, SUBJECT_ID],
                 description="Jenny deleted the subject 'Subject' from report 'Report'."),
            self.report["delta"])

    def test_move_subject(self):
        """Test that a subject can be moved to another report."""
        subject = self.report["subjects"][SUBJECT_ID]
        target_report = dict(_id="target_report", title="Target", report_uuid=REPORT_ID2, subjects={})
        self.database.reports.find_one.side_effect = [self.report, target_report]
        self.assertEqual(dict(ok=True), post_move_subject(SUBJECT_ID, REPORT_ID2, self.database))
        self.assertEqual({}, self.report["subjects"])
        self.assertEqual((SUBJECT_ID, subject), next(iter(target_report["subjects"].items())))
        expected_description = "Jenny moved the subject 'Subject' from report 'Report' to report 'Target'."
        self.assertEqual(
            dict(report_uuid=REPORT_ID, description=expected_description), self.report["delta"])
        self.assertEqual(
            dict(report_uuid=REPORT_ID2, subject_uuid=SUBJECT_ID, description=expected_description),
            target_report["delta"])
