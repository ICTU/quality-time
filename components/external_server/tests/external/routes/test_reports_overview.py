"""Unit tests for the reports routes."""

import unittest
from unittest.mock import Mock, patch

from external.routes import get_reports_overview, post_reports_overview_attribute
from external.routes.plugins.auth_plugin import EDIT_ENTITY_PERMISSION, EDIT_REPORT_PERMISSION

from ...fixtures import METRIC_ID, SOURCE_ID


class ReportsOverviewTest(unittest.TestCase):
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
        inserted = self.database.reports_overviews.insert_one.call_args_list[0][0][0]
        delta = f" from '{old_value}' to '{new_value}'" if old_value and new_value else ""
        description = f"jenny changed the {attribute} of the reports overview{delta}."
        self.assertEqual(dict(email=self.email, description=description), inserted["delta"])

    @patch("bottle.request")
    def test_change_title(self, request):
        """Test that a reports overview title can be changed."""
        request.json = dict(title="All the reports")
        self.assertEqual(dict(ok=True), post_reports_overview_attribute("title", self.database))
        self.assert_change_description("title", "Reports", "All the reports")

    @patch("bottle.request")
    def test_change_title_unchanged(self, request):
        """Test that the reports overview title is not changed if the new value is equal to the old value."""
        request.json = dict(title="Reports")
        self.assertEqual(dict(ok=True), post_reports_overview_attribute("title", self.database))
        self.database.reports_overviews.insert_one.assert_not_called()

    @patch("bottle.request")
    def test_post_unsafe_comment(self, request):
        """Test that comments are sanitized, since they are displayed as inner HTML in the frontend."""
        request.json = dict(comment='Comment with script<script type="text/javascript">alert("Danger")</script>')
        self.assertEqual(dict(ok=True), post_reports_overview_attribute("comment", self.database))
        self.assert_change_description("comment", "None", "Comment with script")

    @patch("bottle.request")
    def test_change_layout(self, request):
        """Test that a reports overview layout can be changed."""
        request.json = dict(layout=[dict(x=1, y=2)])
        self.assertEqual(dict(ok=True), post_reports_overview_attribute("layout", self.database))
        self.assert_change_description("layout")

    @patch("bottle.request")
    def test_change_permission(self, request):
        """Test that the editors can be changed."""
        request.json = dict(permissions={EDIT_ENTITY_PERMISSION: [self.other_mail]})
        self.assertEqual(dict(ok=True), post_reports_overview_attribute("permissions", self.database))
        self.assert_change_description("permissions", "None", f"{{'{EDIT_ENTITY_PERMISSION}': ['{self.other_mail}']}}")

    @patch("bottle.request")
    def test_clear_permissions(self, request):
        """Test that the editors can be cleared."""
        self.database.reports_overviews.find_one.return_value = dict(
            _id="id",
            title="Reports",
            subtitle="",
            permissions={EDIT_REPORT_PERMISSION: [self.other_mail, self.email], EDIT_ENTITY_PERMISSION: [self.email]},
        )
        request.json = dict(permissions={})
        self.assertEqual(dict(ok=True), post_reports_overview_attribute("permissions", self.database))

        old_string = (
            f"{{'{EDIT_REPORT_PERMISSION}': ['{self.other_mail}', '{self.email}'], "
            + f"'{EDIT_ENTITY_PERMISSION}': ['{self.email}']}}"
        )
        self.assert_change_description("permissions", old_string, "{}")

    @patch("bottle.request")
    def test_remove_permissions(self, request):
        """Test that other editors can be removed from the editors."""
        self.database.reports_overviews.find_one.return_value = dict(
            _id="id", title="Reports", subtitle="", permissions={EDIT_REPORT_PERMISSION: [self.other_mail, self.email]}
        )
        request.json = dict(permissions={EDIT_REPORT_PERMISSION: [self.email]})
        self.assertEqual(dict(ok=True), post_reports_overview_attribute("permissions", self.database))
        self.assert_change_description(
            "permissions",
            f"{{'{EDIT_REPORT_PERMISSION}': ['{self.other_mail}', '{self.email}']}}",
            f"{{'{EDIT_REPORT_PERMISSION}': ['{self.email}']}}",
        )

    @patch("bottle.request")
    def test_cannot_remove_own_permission(self, request):
        """Test that other editors can be removed from the editors."""
        self.database.reports_overviews.find_one.return_value = dict(
            _id="id", title="Reports", subtitle="", permissions={EDIT_REPORT_PERMISSION: [self.other_mail, self.email]}
        )
        request.json = dict(permissions={EDIT_REPORT_PERMISSION: [self.other_mail]})
        self.assertEqual(dict(ok=True), post_reports_overview_attribute("permissions", self.database))
        self.assert_change_description(
            "permissions",
            f"{{'{EDIT_REPORT_PERMISSION}': ['{self.other_mail}', '{self.email}']}}",
            f"{{'{EDIT_REPORT_PERMISSION}': ['{self.other_mail}', 'jenny']}}",
        )

    @patch("bottle.request")
    def test_can_remove_own_edit_entity_permission(self, request):
        """Test that editors can remove their entity edit permission."""
        self.database.reports_overviews.find_one.return_value = dict(
            _id="id", title="Reports", subtitle="", permissions={EDIT_ENTITY_PERMISSION: [self.other_mail, self.email]}
        )
        request.json = dict(permissions={EDIT_ENTITY_PERMISSION: [self.other_mail]})
        self.assertEqual(dict(ok=True), post_reports_overview_attribute("permissions", self.database))
        self.assert_change_description(
            "permissions",
            f"{{'{EDIT_ENTITY_PERMISSION}': ['{self.other_mail}', '{self.email}']}}",
            f"{{'{EDIT_ENTITY_PERMISSION}': ['{self.other_mail}']}}",
        )

    def test_get_reports_overview(self):
        """Test that a report can be retrieved and credentials are hidden."""
        self.assertEqual(dict(_id="id", title="Reports", subtitle=""), get_reports_overview(self.database))
