"""Unit tests for the metric routes."""

from unittest.mock import Mock, patch

import requests

from shared_data_model.meta.metric import Unit
from shared_data_model import DATA_MODEL

from model.report import Report

from routes import (
    add_metric_issue,
    delete_metric,
    post_metric_attribute,
    post_metric_copy,
    post_metric_debt,
    post_metric_new,
    post_move_metric,
)
from tests.base import DataModelTestCase, disable_logging
from tests.fixtures import (
    JOHN,
    METRIC_ID,
    METRIC_ID2,
    REPORT_ID,
    REPORT_ID2,
    SOURCE_ID,
    SOURCE_ID2,
    SUBJECT_ID,
    SUBJECT_ID2,
    create_report,
)


class MetricTestCase(DataModelTestCase):
    """Base class for unit tests for the metric routes."""

    def updated_report(self):
        """Return the updated report."""
        return self.database.reports.insert_one.call_args[0][0]


class PostMetricAttributeTestCase(MetricTestCase):
    """Base class for unit tests for the post metric attribute routes."""

    def setUp(self):
        """Extend to set up the database."""
        super().setUp()
        self.report = Report(
            self.DATA_MODEL,
            {
                "_id": "id",
                "report_uuid": REPORT_ID,
                "title": "Report",
                "subjects": {
                    "other_subject": {"metrics": {}},
                    SUBJECT_ID: {
                        "name": "Subject",
                        "metrics": {
                            METRIC_ID: {
                                "name": "name",
                                "type": "security_warnings",
                                "scale": "count",
                                "addition": "sum",
                                "direction": "<",
                                "target": "0",
                                "near_target": "10",
                                "debt_target": None,
                                "accept_debt": False,
                                "tags": [tag.value for tag in DATA_MODEL.metrics["security_warnings"].tags],
                                "sources": {
                                    SOURCE_ID: {"type": "owasp_dependency_check_xml"},
                                    SOURCE_ID2: {"type": "snyk"},
                                },
                            },
                            METRIC_ID2: {"name": "name2", "type": "security_warnings"},
                        },
                    },
                },
            },
        )
        self.database.reports.find.return_value = [self.report]
        self.database.measurements.find.return_value = []
        self.database.measurements.find_one.return_value = {"_id": "id", "metric_uuid": METRIC_ID, "sources": []}
        self.database.sessions.find_one.return_value = JOHN
        self.database.measurements.insert_one.side_effect = self.set_measurement_id

    @staticmethod
    def set_measurement_id(measurement) -> None:
        """Simulate Mongo setting an id on the inserted measurement."""
        measurement["_id"] = "measurement_id"

    def assert_delta(
        self,
        description: str,
        uuids: list[str] | None = None,
        email: str = JOHN["email"],
        report: Report | None = None,
    ):
        """Assert that the report delta contains the correct data."""
        report_to_check = self.report if report is None else report
        uuids = sorted(uuids or [REPORT_ID, SUBJECT_ID, METRIC_ID])
        description = f"John Doe changed the {description}."
        self.assertDictEqual({"uuids": uuids, "email": email, "description": description}, report_to_check["delta"])

    def create_measurement(self, debt_target: str | None = None, status: str | None = None, target: str = "10"):
        """Create a measurement fixture."""
        return {
            "end": "2019-01-01",
            "sources": [],
            "start": "2019-01-01",
            "metric_uuid": METRIC_ID,
            "count": {
                "status": status,
                "status_start": "2019-01-01",
                "value": None,
                "target": target,
                "near_target": "10",
                "debt_target": debt_target,
                "direction": "<",
            },
        }


@patch("bottle.request")
class PostMetricAttributeTest(PostMetricAttributeTestCase):
    """Unit tests for the post metric attribute route."""

    def test_post_metric_name(self, request):
        """Test that the metric name can be changed."""
        request.json = {"name": "ABC"}
        self.assertEqual({"ok": True}, post_metric_attribute(METRIC_ID, "name", self.database))
        updated_report = self.updated_report()
        self.assertEqual("ABC", updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["name"])
        self.assert_delta(
            "name of metric 'name' of subject 'Subject' in report 'Report' from 'name' to 'ABC'",
            report=updated_report,
        )

    @patch("shared.model.measurement.iso_timestamp", new=Mock(return_value="2019-01-01"))
    def test_post_metric_type(self, request):
        """Test that the metric type can be changed and that sources are not removed."""
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["tags"].append("user-supplied tag")
        sources = [
            {"source_uuid": SOURCE_ID, "parse_error": None, "connection_error": None, "value": "0"},
            {"source_uuid": SOURCE_ID2, "parse_error": None, "connection_error": None, "value": "0"},
        ]
        previous_measurement = {
            "_id": "id",
            "metric_uuid": METRIC_ID,
            "sources": sources,
            "count": {
                "status": "target_met",
                "value": "0",
                "target": "0",
                "near_target": "10",
                "debt_target": None,
                "direction": "<",
            },
        }
        self.database.measurements.find_one.return_value = previous_measurement
        expected_new_measurement = self.create_measurement(target="0")
        expected_new_measurement["sources"].extend(
            [
                {"source_uuid": SOURCE_ID, "parse_error": None, "connection_error": None, "value": "0"},
                {"source_uuid": SOURCE_ID2, "parse_error": None, "connection_error": None, "value": "0"},
            ]
        )
        expected_new_measurement["percentage"] = {
            "status_start": "2019-01-01",
            "status": None,
            "direction": "<",
            "value": None,
        }
        request.json = {"type": "dependencies"}
        self.assertDictEqual(expected_new_measurement, post_metric_attribute(METRIC_ID, "type", self.database))
        updated_report = self.updated_report()
        updated_metric = updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]
        self.assertEqual(
            {SOURCE_ID: {"type": "owasp_dependency_check_xml"}, SOURCE_ID2: {"type": "snyk"}},
            updated_metric["sources"],
        )
        self.assertEqual(["maintainability", "user-supplied tag"], updated_metric["tags"])
        self.assert_delta(
            "type of metric 'name' of subject 'Subject' in report 'Report' from 'security_warnings' to 'dependencies'",
            report=updated_report,
        )

    def test_post_metric_target_without_measurements(self, request):
        """Test that changing the metric target does not add a new measurement if none exist."""
        self.database.measurements.find_one.return_value = None
        request.json = {"target": "10"}
        self.assertEqual({"ok": True}, post_metric_attribute(METRIC_ID, "target", self.database))
        self.assert_delta(
            "target of metric 'name' of subject 'Subject' in report 'Report' from '0' to '10'",
            report=self.updated_report(),
        )

    @patch("shared.model.measurement.iso_timestamp", new=Mock(return_value="2019-01-01"))
    def test_post_metric_target_with_measurements(self, request):
        """Test that changing the metric target adds a new measurement if one or more exist."""
        request.json = {"target": "10"}
        self.assertDictEqual(self.create_measurement(), post_metric_attribute(METRIC_ID, "target", self.database))
        self.assert_delta(
            "target of metric 'name' of subject 'Subject' in report 'Report' from '0' to '10'",
            report=self.updated_report(),
        )

    @patch("shared.model.measurement.iso_timestamp", new=Mock(return_value="2019-01-01"))
    def test_post_metric_technical_debt(self, request):
        """Test that accepting technical debt also sets the technical debt value."""
        request.json = {"accept_debt": True}
        self.assertDictEqual(
            self.create_measurement(status="debt_target_met", target="0"),
            post_metric_attribute(METRIC_ID, "accept_debt", self.database),
        )
        self.assert_delta(
            "accept_debt of metric 'name' of subject 'Subject' in report 'Report' from '' to 'True'",
            report=self.updated_report(),
        )

    @patch("shared.model.measurement.iso_timestamp", new=Mock(return_value="2019-01-01"))
    def test_post_metric_technical_debt_without_sources(self, request):
        """Test that accepting technical debt when the metric has no sources also sets the status to debt target met."""
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"] = {}
        request.json = {"accept_debt": True}
        self.assertDictEqual(
            self.create_measurement(status="debt_target_met", target="0"),
            post_metric_attribute(METRIC_ID, "accept_debt", self.database),
        )
        self.assert_delta(
            "accept_debt of metric 'name' of subject 'Subject' in report 'Report' from '' to 'True'",
            report=self.updated_report(),
        )

    @patch("shared.model.measurement.iso_timestamp", new=Mock(return_value="2019-01-01"))
    def test_post_metric_debt_end_date_with_measurements(self, request):
        """Test that changing the metric debt end date adds a new measurement if one or more exist."""
        request.json = {"debt_end_date": "2019-06-07"}
        self.assertDictEqual(
            self.create_measurement(target="0"),
            post_metric_attribute(METRIC_ID, "debt_end_date", self.database),
        )
        self.assert_delta(
            "debt_end_date of metric 'name' of subject 'Subject' in report 'Report' from '' to '2019-06-07'",
            report=self.updated_report(),
        )

    def test_post_unsafe_comment(self, request):
        """Test that comments are sanitized, since they are displayed as inner HTML in the frontend."""
        request.json = {"comment": 'Comment with script<script type="text/javascript">alert("Danger")</script>'}
        self.assertEqual({"ok": True}, post_metric_attribute(METRIC_ID, "comment", self.database))
        updated_report = self.updated_report()
        self.assertEqual("Comment with script", updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["comment"])
        self.assert_delta(
            "comment of metric 'name' of subject 'Subject' in report 'Report' from '' to 'Comment with script'",
            report=updated_report,
        )

    def test_post_comment_with_link(self, request):
        """Test that urls in comments are transformed into anchors."""
        request.json = {"comment": "Comment with url https://google.com"}
        self.assertEqual({"ok": True}, post_metric_attribute(METRIC_ID, "comment", self.database))
        updated_report = self.updated_report()
        self.assertEqual(
            'Comment with url <a href="https://google.com" target="_blank">https://google.com</a>',
            updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["comment"],
        )
        self.assert_delta(
            """comment of metric 'name' of subject 'Subject' in report 'Report' from '' to 'Comment with url """
            """<a href="https://google.com" target="_blank">https://google.com</a>'""",
            report=updated_report,
        )

    def test_post_position_first(self, request):
        """Test that a metric can be moved to the top of the list."""
        request.json = {"position": "first"}
        self.assertEqual({"ok": True}, post_metric_attribute(METRIC_ID2, "position", self.database))
        self.assertEqual([METRIC_ID2, METRIC_ID], list(self.report["subjects"][SUBJECT_ID]["metrics"].keys()))
        self.assert_delta(
            "position of metric 'name2' of subject 'Subject' in report 'Report' from '1' to '0'",
            uuids=[REPORT_ID, SUBJECT_ID, METRIC_ID2],
            report=self.updated_report(),
        )

    def test_post_position_last(self, request):
        """Test that a metric can be moved to the bottom of the list."""
        request.json = {"position": "last"}
        self.assertEqual({"ok": True}, post_metric_attribute(METRIC_ID, "position", self.database))
        self.assertEqual([METRIC_ID2, METRIC_ID], list(self.report["subjects"][SUBJECT_ID]["metrics"].keys()))
        self.assert_delta(
            "position of metric 'name' of subject 'Subject' in report 'Report' from '0' to '1'",
            report=self.updated_report(),
        )

    def test_post_position_previous(self, request):
        """Test that a metric can be moved up."""
        request.json = {"position": "previous"}
        self.assertEqual({"ok": True}, post_metric_attribute(METRIC_ID2, "position", self.database))
        self.assertEqual([METRIC_ID2, METRIC_ID], list(self.report["subjects"][SUBJECT_ID]["metrics"].keys()))
        self.assert_delta(
            "position of metric 'name2' of subject 'Subject' in report 'Report' from '1' to '0'",
            uuids=[REPORT_ID, SUBJECT_ID, METRIC_ID2],
            report=self.updated_report(),
        )

    def test_post_position_next(self, request):
        """Test that a metric can be moved down."""
        request.json = {"position": "next"}
        self.assertEqual({"ok": True}, post_metric_attribute(METRIC_ID, "position", self.database))
        self.assertEqual([METRIC_ID2, METRIC_ID], list(self.report["subjects"][SUBJECT_ID]["metrics"].keys()))
        self.assert_delta(
            "position of metric 'name' of subject 'Subject' in report 'Report' from '0' to '1'",
            report=self.updated_report(),
        )

    def test_post_position_first_previous(self, request):
        """Test that moving the first metric up does nothing."""
        request.json = {"position": "previous"}
        self.assertEqual({"ok": True}, post_metric_attribute(METRIC_ID, "position", self.database))
        self.database.reports.insert_one.assert_not_called()
        self.assertEqual([METRIC_ID, METRIC_ID2], list(self.report["subjects"][SUBJECT_ID]["metrics"].keys()))

    def test_post_position_last_next(self, request):
        """Test that moving the last metric down does nothing."""
        request.json = {"position": "next"}
        self.assertEqual({"ok": True}, post_metric_attribute(METRIC_ID2, "position", self.database))
        self.database.reports.insert_one.assert_not_called()
        self.assertEqual([METRIC_ID, METRIC_ID2], list(self.report["subjects"][SUBJECT_ID]["metrics"].keys()))

    def test_post_position_index(self, request):
        """Test that a metric can be moved to a specific index."""
        request.json = {"position_index": 1}
        self.assertEqual({"ok": True}, post_metric_attribute(METRIC_ID, "position_index", self.database))
        self.database.reports.insert_one.assert_called_once()
        self.assertEqual([METRIC_ID2, METRIC_ID], list(self.report["subjects"][SUBJECT_ID]["metrics"].keys()))


@patch("bottle.request")
class PostMetricDebtTest(PostMetricAttributeTestCase):
    """Unit tests for the post metric debt route."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        super().setUp()
        self.database.measurements.find_one.return_value = None

    @patch("shared.model.measurement.iso_timestamp", new=Mock(return_value="2019-01-01"))
    def test_turn_metric_technical_debt_on_with_existing_measurement(self, request):
        """Test that accepting technical debt also sets the technical debt value."""
        self.database.measurements.find_one.return_value = {
            "_id": "id",
            "metric_uuid": METRIC_ID,
            "count": {"value": "100", "status_start": "2018-01-01"},
            "sources": [],
        }
        request.json = {"accept_debt": True}
        self.assertDictEqual(
            self.create_measurement(debt_target="100", status="debt_target_met", target="0"),
            post_metric_debt(METRIC_ID, self.database),
        )
        updated_report = self.updated_report()
        expected_date = Report(self.DATA_MODEL, updated_report).deadline("debt_target_met")
        self.assert_delta(
            "accepted debt from 'False' to 'True' and the debt target from 'None' to '100' and the debt end date from "
            f"'None' to '{expected_date}' of metric 'name' of subject 'Subject' in report 'Report'",
            report=updated_report,
        )
        self.assertTrue(updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["accept_debt"])

    @patch("shared.model.measurement.iso_timestamp", new=Mock(return_value="2019-01-01"))
    def test_turn_metric_technical_debt_on_with_existing_measurement_but_without_desired_response_time(self, request):
        """Test that accepting technical debt also sets the technical debt value, but not the deadline."""
        self.report["desired_response_times"] = {"debt_target_met": None}
        self.database.measurements.find_one.return_value = {
            "_id": "id",
            "metric_uuid": METRIC_ID,
            "count": {"value": "100", "status_start": "2018-01-01"},
            "sources": [],
        }
        request.json = {"accept_debt": True}
        self.assertDictEqual(
            self.create_measurement(debt_target="100", status="debt_target_met", target="0"),
            post_metric_debt(METRIC_ID, self.database),
        )
        updated_report = self.updated_report()
        self.assert_delta(
            "accepted debt from 'False' to 'True' and the debt target from 'None' to '100' "
            "of metric 'name' of subject 'Subject' in report 'Report'",
            report=updated_report,
        )
        self.assertTrue(updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["accept_debt"])

    def test_turn_metric_technical_debt_on_without_existing_measurement(self, request):
        """Test that accepting technical debt also sets the technical debt value."""
        request.json = {"accept_debt": True}
        self.assertDictEqual({"ok": True}, post_metric_debt(METRIC_ID, self.database))
        updated_report = self.updated_report()
        expected_date = Report(self.DATA_MODEL, updated_report).deadline("debt_target_met")
        self.assert_delta(
            f"accepted debt from 'False' to 'True' and the debt end date from 'None' to '{expected_date}' "
            "of metric 'name' of subject 'Subject' in report 'Report'",
            report=updated_report,
        )
        self.assertTrue(updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["accept_debt"])
        self.assertEqual(expected_date, updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["debt_end_date"])

    def test_turn_metric_technical_debt_off_that_is_already_off(self, request):
        """Test that turning debt off when it's already off does nothing."""
        request.json = {"accept_debt": False}
        self.assertDictEqual({"ok": True}, post_metric_debt(METRIC_ID, self.database))
        self.database.reports.insert_one.assert_not_called()

    def test_turn_metric_technical_debt_off_that_is_already_off_but_has_debt_target(self, request):
        """Test that turning debt off when it's already off does reset debt target."""
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["debt_target"] = "100"
        request.json = {"accept_debt": False}
        self.assertDictEqual({"ok": True}, post_metric_debt(METRIC_ID, self.database))
        updated_report = self.updated_report()
        self.assert_delta(
            "debt target from '100' to 'None' of metric 'name' of subject 'Subject' in report 'Report'",
            report=updated_report,
        )
        self.assertFalse(updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["accept_debt"])
        self.assertEqual(None, updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["debt_target"])

    def test_turn_metric_technical_debt_off_that_is_already_off_but_has_debt_end_date(self, request):
        """Test that turning debt off when it's already off does reset debt end date."""
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["debt_end_date"] = "2000-01-01"
        request.json = {"accept_debt": False}
        self.assertDictEqual({"ok": True}, post_metric_debt(METRIC_ID, self.database))
        updated_report = self.updated_report()
        self.assert_delta(
            "debt end date from '2000-01-01' to 'None' of metric 'name' of subject 'Subject' in report 'Report'",
            report=updated_report,
        )
        self.assertFalse(updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["accept_debt"])
        self.assertFalse(updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["debt_end_date"])

    def test_turn_metric_technical_debt_off_without_existing_measurement(self, request):
        """Test turning technical debt off."""
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["accept_debt"] = True
        request.json = {"accept_debt": False}
        self.assertDictEqual({"ok": True}, post_metric_debt(METRIC_ID, self.database))
        updated_report = self.updated_report()
        self.assert_delta(
            "accepted debt from 'True' to 'False' of metric 'name' of subject 'Subject' in report 'Report'",
            report=updated_report,
        )
        self.assertFalse(updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["accept_debt"])


class MetricTest(MetricTestCase):
    """Unit tests for adding and deleting metrics."""

    def setUp(self):
        """Extend to set up the report fixture."""
        super().setUp()
        self.report = Report(self.DATA_MODEL, create_report())
        self.database.reports.find.return_value = [self.report]
        self.database.measurements.find.return_value = []
        self.database.sessions.find_one.return_value = JOHN

    def assert_delta(self, description: str, uuids: list[str] | None = None, email: str = JOHN["email"], report=None):
        """Assert that the report delta contains the correct data."""
        uuids = sorted(uuids or [REPORT_ID, SUBJECT_ID, METRIC_ID])
        report = report or self.report
        self.assertEqual({"uuids": uuids, "email": email, "description": description}, report["delta"])

    @patch("bottle.request")
    def test_add_metric(self, request):
        """Test that a metric can be added."""
        request.json = {"type": "violations"}
        self.assertTrue(post_metric_new(SUBJECT_ID, self.database)["ok"])
        updated_report = self.updated_report()
        metric_uuid = list(self.report["subjects"][SUBJECT_ID]["metrics"].keys())[1]
        self.assertEqual("violations", updated_report["subjects"][SUBJECT_ID]["metrics"][metric_uuid]["type"])
        self.assert_delta(
            "John Doe added a new metric to subject 'Subject' in report 'Report'.",
            uuids=[REPORT_ID, SUBJECT_ID, metric_uuid],
            report=updated_report,
        )

    def test_copy_metric(self):
        """Test that a metric can be copied."""
        self.assertTrue(post_metric_copy(METRIC_ID, SUBJECT_ID, self.database)["ok"])
        self.database.reports.insert_one.assert_called_once()
        updated_report = self.updated_report()
        inserted_metrics = updated_report["subjects"][SUBJECT_ID]["metrics"]
        self.assertEqual(2, len(inserted_metrics))
        self.assert_delta(
            "John Doe copied the metric 'Metric' of subject 'Subject' from report 'Report' to subject 'Subject' in "
            "report 'Report'.",
            uuids=[REPORT_ID, SUBJECT_ID, list(inserted_metrics.keys())[1]],
            report=updated_report,
        )

    def test_move_metric_within_report(self):
        """Test that a metric can be moved to a different subject in the same report."""
        metric = self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]
        target_subject = self.report["subjects"][SUBJECT_ID2] = {"name": "Target", "metrics": {}}
        self.assertEqual({"ok": True}, post_move_metric(METRIC_ID, SUBJECT_ID2, self.database))
        updated_report = self.updated_report()
        self.assertEqual({}, updated_report["subjects"][SUBJECT_ID]["metrics"])
        self.assertEqual((METRIC_ID, metric), next(iter(target_subject["metrics"].items())))
        self.assert_delta(
            "John Doe moved the metric 'Metric' from subject 'Subject' in report 'Report' to subject 'Target' in "
            "report 'Report'.",
            uuids=[REPORT_ID, SUBJECT_ID, SUBJECT_ID2, METRIC_ID],
            report=updated_report,
        )

    def test_move_metric_across_reports(self):
        """Test that a metric can be moved to a different subject in a different report."""
        metric = self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]
        target_subject = {"name": "Target", "metrics": {}}
        target_report = {
            "_id": "target_report",
            "title": "Target",
            "report_uuid": REPORT_ID2,
            "subjects": {SUBJECT_ID2: target_subject},
        }
        self.database.reports.find.return_value = [self.report, target_report]
        self.assertEqual({"ok": True}, post_move_metric(METRIC_ID, SUBJECT_ID2, self.database))
        updated_reports = self.database.reports.insert_many.call_args[0][0]
        self.assertEqual({}, self.report["subjects"][SUBJECT_ID]["metrics"])
        self.assertEqual((METRIC_ID, metric), next(iter(target_subject["metrics"].items())))
        expected_description = (
            "John Doe moved the metric 'Metric' from subject 'Subject' in report 'Report' to subject 'Target' in "
            "report 'Target'."
        )
        expected_uuids = [REPORT_ID, REPORT_ID2, SUBJECT_ID, SUBJECT_ID2, METRIC_ID]

        for report in updated_reports:
            self.assert_delta(expected_description, uuids=expected_uuids, report=report)

    def test_delete_metric(self):
        """Test that the metric can be deleted."""
        self.assertEqual({"ok": True}, delete_metric(METRIC_ID, self.database))
        updated_report = self.updated_report()
        self.assertEqual({}, updated_report["subjects"][SUBJECT_ID]["metrics"])
        self.assert_delta(
            "John Doe deleted metric 'Metric' from subject 'Subject' in report 'Report'.",
            report=updated_report,
        )


@patch("model.issue_tracker.requests.post")
class MetricIssueTest(DataModelTestCase):
    """Unit tests for metric issue routes."""

    METRIC_URL = "https://quality_time/metric42"
    ISSUE_URL = "https://tracker/browse/FOO-42"

    def setUp(self):
        """Extend to set up the report fixture."""
        super().setUp()
        self.sources = {
            SOURCE_ID: {"name": "Source", "type": "owasp_zap", "parameters": {"url": "https://zap"}},
        }
        self.report = Report(
            self.DATA_MODEL,
            {
                "report_uuid": REPORT_ID,
                "issue_tracker": {"parameters": {"url": "https://tracker", "project_key": "KEY", "issue_type": "BUG"}},
                "subjects": {
                    SUBJECT_ID: {
                        "name": "Subject",
                        "metrics": {
                            METRIC_ID: {
                                "type": "violations",
                                "name": "name",
                                "unit": Unit.VIOLATIONS,
                                "sources": self.sources,
                            },
                        },
                    },
                },
            },
        )
        self.database.reports.find.return_value = [self.report]
        self.database.sessions.find_one.return_value = JOHN
        self.measurement = {
            "_id": "id",
            "metric_uuid": METRIC_ID,
            "count": {"status": "target_not_met", "value": "42"},
            "sources": [{"source_uuid": SOURCE_ID, "parse_error": None, "connection_error": None, "value": "42"}],
        }
        self.database.measurements.find_one.return_value = self.measurement
        self.expected_json = {
            "fields": {
                "project": {"key": "KEY"},
                "issuetype": {"name": "BUG"},
                "summary": "Fix 42 violations from Source",
                "description": "The metric [name|https://quality_time/metric42] in Quality-time reports 42 violations "
                "from Source.\nPlease go to https://zap for more details.\n",
            },
        }

    def assert_issue_posted(self, method):
        """Check that method is called to post the issue data to the issue tracker."""
        issue_api = "https://tracker/rest/api/2/issue"
        method.assert_called_once_with(issue_api, auth=None, headers={}, json=self.expected_json, timeout=10)

    def assert_issue_inserted(self):
        """Check that the issue is inserted in the database."""
        inserted_report = self.database.reports.insert_one.call_args_list[0][0][0]
        inserted_issue_ids = inserted_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["issue_ids"]
        self.assertEqual(["FOO-42"], inserted_issue_ids)

    @patch("bottle.request", Mock(json={"metric_url": METRIC_URL}))
    def test_add_metric_issue(self, requests_post):
        """Test that an issue can be added to the issue tracker."""
        response = Mock()
        response.json.return_value = {"key": "FOO-42"}
        requests_post.return_value = response
        self.assertEqual({"ok": True, "issue_url": self.ISSUE_URL}, add_metric_issue(METRIC_ID, self.database))
        self.assert_issue_posted(requests_post)
        self.assert_issue_inserted()

    @patch("bottle.request", Mock(json={"metric_url": METRIC_URL}))
    def test_add_metric_issue_with_landing_url(self, requests_post):
        """Test that the metric landing URL is used if available."""
        self.sources[SOURCE_ID]["parameters"]["landing_url"] = "https://zap/landing"
        description = self.expected_json["fields"]["description"]
        self.expected_json["fields"]["description"] = description.replace("https://zap", "https://zap/landing")
        response = Mock()
        response.json.return_value = {"key": "FOO-42"}
        requests_post.return_value = response
        self.assertEqual({"ok": True, "issue_url": self.ISSUE_URL}, add_metric_issue(METRIC_ID, self.database))
        self.assert_issue_posted(requests_post)
        self.assert_issue_inserted()

    @patch("bottle.request", Mock(json={"metric_url": METRIC_URL}))
    def test_add_metric_issue_with_percentage_scale(self, requests_post):
        """Test that an issue with the percentage scale can be added to the issue tracker."""
        self.measurement["percentage"] = {"status": "target_not_met", "value": "21"}
        self.expected_json["fields"]["summary"] = "Fix 21% violations from Source"
        self.expected_json["fields"]["description"] = (
            "The metric [name|https://quality_time/metric42] in Quality-time reports 21% violations "
            "from Source.\nPlease go to https://zap for more details.\n"
        )
        self.report.metrics_dict[METRIC_ID]["scale"] = "percentage"
        response = Mock()
        response.json.return_value = {"key": "FOO-42"}
        requests_post.return_value = response
        self.assertEqual({"ok": True, "issue_url": self.ISSUE_URL}, add_metric_issue(METRIC_ID, self.database))
        self.assert_issue_posted(requests_post)
        self.assert_issue_inserted()

    @patch("bottle.request", Mock(json={"metric_url": METRIC_URL}))
    @patch("model.issue_tracker.requests.get")
    def test_add_metric_issue_with_labels(self, requests_get, requests_post):
        """Test that an issue can be added to the issue tracker."""
        self.report["issue_tracker"]["parameters"]["issue_labels"] = ["label", "label with spaces"]
        project_response = Mock()
        project_response.json.return_value = [{"key": "KEY", "name": "Foo"}]
        issue_types_response = Mock()
        issue_types_response.json.return_value = {"values": [{"id": "1", "name": "BUG", "subtask": False}]}
        fields_response = Mock()
        fields_response.json.return_value = {"values": [{"fieldId": "labels", "name": "Labels"}]}
        requests_get.side_effect = [project_response, issue_types_response, fields_response]
        response = Mock()
        response.json.return_value = {"key": "FOO-42"}
        requests_post.return_value = response
        self.assertEqual({"ok": True, "issue_url": self.ISSUE_URL}, add_metric_issue(METRIC_ID, self.database))
        self.expected_json["fields"]["labels"] = ["label", "label_with_spaces"]
        self.assert_issue_posted(requests_post)
        self.assert_issue_inserted()

    @patch("bottle.request", Mock(json={"metric_url": METRIC_URL}))
    @disable_logging
    @patch("model.issue_tracker.requests.get")
    def test_add_metric_issue_with_epic_link(self, requests_get, requests_post):
        """Test that an issue can be added to the issue tracker."""
        self.report["issue_tracker"]["parameters"]["epic_link"] = "FOO-420"
        project_response = Mock()
        project_response.json.return_value = [{"key": "KEY", "name": "Foo"}]
        issue_types_response = Mock()
        issue_types_response.json.return_value = {"values": [{"id": "1", "name": "BUG", "subtask": False}]}
        fields_response = Mock()
        fields_response.json.return_value = {"values": [{"fieldId": "epic_link_field_id", "name": "Epic Link"}]}
        epic_links_response = Mock()
        epic_links_response.json.return_value = {
            "issues": [{"key": "FOO-420", "fields": {"summary": "FOO-420 Summary"}}],
        }
        requests_get.side_effect = [project_response, issue_types_response, fields_response, epic_links_response]
        response = Mock()
        response.json.return_value = {"key": "FOO-42"}
        requests_post.return_value = response
        self.assertEqual({"ok": True, "issue_url": self.ISSUE_URL}, add_metric_issue(METRIC_ID, self.database))
        self.expected_json["fields"]["epic_link_field_id"] = "FOO-420"
        self.assert_issue_posted(requests_post)
        self.assert_issue_inserted()

    @patch("bottle.request", Mock(json={"metric_url": METRIC_URL}))
    @disable_logging
    def test_add_metric_issue_failure(self, requests_post):
        """Test that an error message is returned if an issue cannot be added to the issue tracker."""
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError("Oops")
        requests_post.return_value = response
        self.assertEqual({"ok": False, "error": "Oops"}, add_metric_issue(METRIC_ID, self.database))
