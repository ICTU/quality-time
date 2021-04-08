"""Unit tests for the reports routes."""

import unittest
from unittest.mock import Mock, patch
from routes.plugins.auth_plugin import EDIT_ENTITY_PERMISSION, EDIT_REPORT_PERMISSION

from routes.reports import get_reports, post_reports_attribute

from ..fixtures import METRIC_ID, REPORT_ID, SOURCE_ID, SUBJECT_ID, create_report


class ReportsTest(unittest.TestCase):
    """Unit tests for the reports routes."""

    def setUp(self):
        """Override to set up a mock database with contents."""
        self.database = Mock()
        self.email = "jenny@example.org"
        self.other_mail = "john@example.org"
        self.database.sessions.find_one.return_value = dict(user="jenny", email=self.email)
        self.database.datamodels.find_one.return_value = dict(
            _id="id",
            sources=dict(source_type=dict(parameters=dict(url=dict(type="url"), password=dict(type="password")))),
            metrics=dict(metric_type=dict(default_scale="count")),
        )
        self.database.reports_overviews.find_one.return_value = dict(_id="id", title="Reports", subtitle="")
        self.measurement = dict(
            _id="id",
            metric_uuid=METRIC_ID,
            count=dict(status="target_not_met"),
            sources=[dict(source_uuid=SOURCE_ID, parse_error=None, connection_error=None, value="42")],
        )
        self.database.measurements.find.return_value = [self.measurement]

    def assert_change_description(self, attribute: str, old_value=None, new_value=None) -> None:
        """Assert that a change description is added to the new reports overview."""
        inserted = self.database.reports_overviews.insert.call_args_list[0][0][0]
        delta = f" from '{old_value}' to '{new_value}'" if old_value and new_value else ""
        description = f"jenny changed the {attribute} of the reports overview{delta}."
        self.assertEqual(dict(email=self.email, description=description), inserted["delta"])

    @patch("bottle.request")
    def test_post_reports_attribute_title(self, request):
        """Test that a reports (overview) attribute can be changed."""
        request.json = dict(title="All the reports")
        self.assertEqual(dict(ok=True), post_reports_attribute("title", self.database))
        self.assert_change_description("title", "Reports", "All the reports")

    @patch("bottle.request")
    def test_post_reports_attribute_title_unchanged(self, request):
        """Test that the reports (overview) attribute is not changed if the new value is equal to the old value."""
        request.json = dict(title="Reports")
        self.assertEqual(dict(ok=True), post_reports_attribute("title", self.database))
        self.database.reports_overviews.insert.assert_not_called()

    @patch("bottle.request")
    def test_post_reports_attribute_layout(self, request):
        """Test that a reports (overview) layout can be changed."""
        request.json = dict(layout=[dict(x=1, y=2)])
        self.assertEqual(dict(ok=True), post_reports_attribute("layout", self.database))
        self.assert_change_description("layout")

    @patch("bottle.request")
    def test_post_reports_report_permission(self, request):
        """Test that the reports (overview) editors can be changed."""
        request.json = dict(permissions={EDIT_ENTITY_PERMISSION: [self.other_mail]})
        self.assertEqual(dict(ok=True), post_reports_attribute("permissions", self.database))
        self.assert_change_description("permissions", "None", f"{{'{EDIT_ENTITY_PERMISSION}': ['{self.other_mail}']}}")

    @patch("bottle.request")
    def test_post_reports_attribute_permissions_clear(self, request):
        """Test that the reports (overview) editors can be cleared."""
        self.database.reports_overviews.find_one.return_value = dict(
            _id="id",
            title="Reports",
            subtitle="",
            permissions={EDIT_REPORT_PERMISSION: [self.other_mail, self.email], EDIT_ENTITY_PERMISSION: [self.email]},
        )
        request.json = dict(permissions={})
        self.assertEqual(dict(ok=True), post_reports_attribute("permissions", self.database))

        old_string = f"{{'{EDIT_REPORT_PERMISSION}': ['{self.other_mail}', '{self.email}'], '{EDIT_ENTITY_PERMISSION}': ['{self.email}']}}"
        self.assert_change_description("permissions", old_string, "{}")

    @patch("bottle.request")
    def test_post_reports_attribute_editors_remove_others(self, request):
        """Test that other editors can be removed from the reports (overview) editors."""
        self.database.reports_overviews.find_one.return_value = dict(
            _id="id", title="Reports", subtitle="", permissions={EDIT_REPORT_PERMISSION: [self.other_mail, self.email]}
        )
        request.json = dict(permissions={EDIT_REPORT_PERMISSION: [self.email]})
        self.assertEqual(dict(ok=True), post_reports_attribute("permissions", self.database))
        self.assert_change_description(
            "permissions",
            f"{{'{EDIT_REPORT_PERMISSION}': ['{self.other_mail}', '{self.email}']}}",
            f"{{'{EDIT_REPORT_PERMISSION}': ['{self.email}']}}",
        )

    @patch("bottle.request")
    def test_post_reports_report_permission_editors_cannot_remove_self(self, request):
        """Test that other editors can be removed from the reports (overview) editors."""
        self.database.reports_overviews.find_one.return_value = dict(
            _id="id", title="Reports", subtitle="", permissions={EDIT_REPORT_PERMISSION: [self.other_mail, self.email]}
        )
        request.json = dict(permissions={EDIT_REPORT_PERMISSION: [self.other_mail]})
        self.assertEqual(dict(ok=True), post_reports_attribute("permissions", self.database))
        self.assert_change_description(
            "permissions",
            f"{{'{EDIT_REPORT_PERMISSION}': ['{self.other_mail}', '{self.email}']}}",
            f"{{'{EDIT_REPORT_PERMISSION}': ['{self.other_mail}', '{self.email}']}}",
        )

    @patch("bottle.request")
    def test_post_reports_entity_permission_can_remove_self(self, request):
        """Test that the reports (overview) editors can be changed."""
        self.database.reports_overviews.find_one.return_value = dict(
            _id="id", title="Reports", subtitle="", permissions={EDIT_ENTITY_PERMISSION: [self.other_mail, self.email]}
        )
        request.json = dict(permissions={EDIT_ENTITY_PERMISSION: [self.other_mail]})
        self.assertEqual(dict(ok=True), post_reports_attribute("permissions", self.database))
        self.assert_change_description(
            "permissions",
            f"{{'{EDIT_ENTITY_PERMISSION}': ['{self.other_mail}', '{self.email}']}}",
            f"{{'{EDIT_ENTITY_PERMISSION}': ['{self.other_mail}']}}",
        )

    def test_get_report(self):
        """Test that a report can be retrieved and credentials are hidden."""
        report = create_report()
        self.database.reports.find.return_value = [report]
        report["summary"] = dict(red=0, green=0, yellow=0, grey=0, white=1)
        report["summary_by_subject"] = {SUBJECT_ID: dict(red=0, green=0, yellow=0, grey=0, white=1)}
        report["summary_by_tag"] = {}
        self.assertEqual(dict(_id="id", title="Reports", subtitle="", reports=[report]), get_reports(self.database))

    @patch("bottle.request")
    def test_get_old_report(self, request):
        """Test that an old report can be retrieved and credentials are hidden."""
        request.query = dict(report_date="2020-08-31T23:59:59.000Z")
        report = create_report()
        self.database.reports.distinct.return_value = [REPORT_ID]
        self.database.reports.find_one.return_value = report
        report["summary"] = dict(red=0, green=0, yellow=0, grey=0, white=1)
        report["summary_by_subject"] = {SUBJECT_ID: dict(red=0, green=0, yellow=0, grey=0, white=1)}
        report["summary_by_tag"] = {}
        self.assertEqual(dict(_id="id", title="Reports", subtitle="", reports=[report]), get_reports(self.database))

    def test_status_start(self):
        """Test that the status start is part of the reports summary."""
        self.measurement["count"]["status_start"] = "2020-12-03:22:28:00+00:00"
        report = create_report()
        self.database.reports.find.return_value = [report]
        report["summary"] = dict(red=0, green=0, yellow=0, grey=0, white=1)
        report["summary_by_subject"] = {SUBJECT_ID: dict(red=0, green=0, yellow=0, grey=0, white=1)}
        report["summary_by_tag"] = {}
        self.assertEqual(dict(_id="id", title="Reports", subtitle="", reports=[report]), get_reports(self.database))
