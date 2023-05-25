"""Unit tests for the metric routes."""

from datetime import date, timedelta
from unittest.mock import Mock, patch

import requests
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
from ..base import DataModelTestCase, disable_logging
from ..fixtures import (
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


class PostMetricAttributeTestCase(DataModelTestCase):
    """Base class for unit tests for the post metric attribute routes."""

    def setUp(self):
        """Extend to set up the database."""
        super().setUp()
        self.report = Report(
            self.DATA_MODEL,
            dict(
                _id="id",
                report_uuid=REPORT_ID,
                title="Report",
                subjects={
                    "other_subject": dict(metrics={}),
                    SUBJECT_ID: dict(
                        name="Subject",
                        metrics={
                            METRIC_ID: dict(
                                name="name",
                                type="security_warnings",
                                scale="count",
                                addition="sum",
                                direction="<",
                                target="0",
                                near_target="10",
                                debt_target=None,
                                accept_debt=False,
                                tags=[],
                                sources={SOURCE_ID: dict(type="owasp_dependency_check"), SOURCE_ID2: dict(type="snyk")},
                            ),
                            METRIC_ID2: dict(name="name2", type="security_warnings"),
                        },
                    ),
                },
            ),
        )
        self.database.reports.find.return_value = [self.report]
        self.database.measurements.find.return_value = []
        self.database.sessions.find_one.return_value = JOHN
        self.database.measurements.insert_one.side_effect = self.set_measurement_id

    @staticmethod
    def set_measurement_id(measurement):
        """Simulate Mongo setting an id on the inserted measurement."""
        measurement["_id"] = "measurement_id"

    def assert_delta(
        self, description: str, uuids: list[str] = None, email: str = JOHN["email"], report: Report = None
    ):
        """Assert that the report delta contains the correct data."""
        report = report if report is not None else self.report
        uuids = sorted(uuids or [REPORT_ID, SUBJECT_ID, METRIC_ID])
        description = f"John Doe changed the {description}."
        self.assertDictEqual(dict(uuids=uuids, email=email, description=description), report["delta"])


@patch("bottle.request")
class PostMetricAttributeTest(PostMetricAttributeTestCase):
    """Unit tests for the post metric attribute route."""

    def test_post_metric_name(self, request):
        """Test that the metric name can be changed."""
        request.json = dict(name="ABC")
        self.assertEqual(dict(ok=True), post_metric_attribute(METRIC_ID, "name", self.database))
        self.database.reports.insert_one.assert_called_once_with(self.report)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            "name of metric 'name' of subject 'Subject' in report 'Report' from 'name' to 'ABC'", report=updated_report
        )

    @patch("shared.model.measurement.iso_timestamp", new=Mock(return_value="2019-01-01"))
    def test_post_metric_type(self, request):
        """Test that the metric type can be changed and that sources are not removed."""
        sources = [
            dict(source_uuid=SOURCE_ID, parse_error=None, connection_error=None, value="0"),
            dict(source_uuid=SOURCE_ID2, parse_error=None, connection_error=None, value="0"),
        ]
        previous_measurement = dict(
            _id="id",
            metric_uuid=METRIC_ID,
            sources=sources,
            count=dict(status="target_met", value="0", target="0", near_target="10", debt_target=None, direction="<"),
        )
        self.database.measurements.find_one.return_value = previous_measurement
        expected_new_measurement = dict(
            metric_uuid=METRIC_ID,
            sources=[
                dict(source_uuid=SOURCE_ID, parse_error=None, connection_error=None, value="0"),
                dict(source_uuid=SOURCE_ID2, parse_error=None, connection_error=None, value="0"),
            ],
            count=dict(
                status_start="2019-01-01",
                status=None,
                value=None,
                target="0",
                near_target="10",
                debt_target=None,
                direction="<",
            ),
            percentage=dict(
                status_start="2019-01-01",
                status=None,
                direction="<",
                value=None,
            ),
            end="2019-01-01",
            start="2019-01-01",
        )
        request.json = dict(type="dependencies")
        self.assertDictEqual(expected_new_measurement, post_metric_attribute(METRIC_ID, "type", self.database))
        self.database.reports.insert_one.assert_called_once_with(self.report)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assertEqual(
            {SOURCE_ID: dict(type="owasp_dependency_check"), SOURCE_ID2: dict(type="snyk")},
            updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"],
        )
        self.assert_delta(
            "type of metric 'name' of subject 'Subject' in report 'Report' from 'security_warnings' to 'dependencies'",
            report=updated_report,
        )

    def test_post_metric_target_without_measurements(self, request):
        """Test that changing the metric target does not add a new measurement if none exist."""
        self.database.measurements.find_one.return_value = None
        request.json = dict(target="10")
        self.assertEqual(dict(ok=True), post_metric_attribute(METRIC_ID, "target", self.database))
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            "target of metric 'name' of subject 'Subject' in report 'Report' from '0' to '10'", report=updated_report
        )

    @patch("shared.model.measurement.iso_timestamp", new=Mock(return_value="2019-01-01"))
    def test_post_metric_target_with_measurements(self, request):
        """Test that changing the metric target adds a new measurement if one or more exist."""
        self.database.measurements.find_one.return_value = dict(_id="id", metric_uuid=METRIC_ID, sources=[])
        request.json = dict(target="10")
        self.assertDictEqual(
            dict(
                end="2019-01-01",
                sources=[],
                start="2019-01-01",
                metric_uuid=METRIC_ID,
                count=dict(
                    status=None,
                    status_start="2019-01-01",
                    value=None,
                    target="10",
                    near_target="10",
                    debt_target=None,
                    direction="<",
                ),
            ),
            post_metric_attribute(METRIC_ID, "target", self.database),
        )
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            "target of metric 'name' of subject 'Subject' in report 'Report' from '0' to '10'", report=updated_report
        )

    @patch("shared.model.measurement.iso_timestamp", new=Mock(return_value="2019-01-01"))
    def test_post_metric_technical_debt(self, request):
        """Test that accepting technical debt also sets the technical debt value."""
        self.database.measurements.find_one.return_value = dict(_id="id", metric_uuid=METRIC_ID, sources=[])
        request.json = dict(accept_debt=True)
        self.assertDictEqual(
            dict(
                end="2019-01-01",
                sources=[],
                start="2019-01-01",
                metric_uuid=METRIC_ID,
                count=dict(
                    value=None,
                    status=None,
                    status_start="2019-01-01",
                    target="0",
                    near_target="10",
                    debt_target=None,
                    direction="<",
                ),
            ),
            post_metric_attribute(METRIC_ID, "accept_debt", self.database),
        )
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            "accept_debt of metric 'name' of subject 'Subject' in report 'Report' from '' to 'True'",
            report=updated_report,
        )

    @patch("shared.model.measurement.iso_timestamp", new=Mock(return_value="2019-01-01"))
    def test_post_metric_technical_debt_without_sources(self, request):
        """Test that accepting technical debt when the metric has no sources also sets the status to debt target met."""
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"] = {}
        self.database.measurements.find_one.return_value = dict(_id="id", metric_uuid=METRIC_ID, sources=[])
        request.json = dict(accept_debt=True)
        self.assertDictEqual(
            dict(
                end="2019-01-01",
                sources=[],
                start="2019-01-01",
                metric_uuid=METRIC_ID,
                count=dict(
                    value=None,
                    status="debt_target_met",
                    status_start="2019-01-01",
                    target="0",
                    near_target="10",
                    debt_target=None,
                    direction="<",
                ),
            ),
            post_metric_attribute(METRIC_ID, "accept_debt", self.database),
        )
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            "accept_debt of metric 'name' of subject 'Subject' in report 'Report' from '' to 'True'",
            report=updated_report,
        )

    @patch("shared.model.measurement.iso_timestamp", new=Mock(return_value="2019-01-01"))
    def test_post_metric_debt_end_date_with_measurements(self, request):
        """Test that changing the metric debt end date adds a new measurement if one or more exist."""
        self.database.measurements.find_one.return_value = dict(_id="id", metric_uuid=METRIC_ID, sources=[])
        request.json = dict(debt_end_date="2019-06-07")
        count = dict(
            value=None,
            status=None,
            status_start="2019-01-01",
            target="0",
            near_target="10",
            debt_target=None,
            direction="<",
        )
        new_measurement = dict(end="2019-01-01", sources=[], start="2019-01-01", metric_uuid=METRIC_ID, count=count)
        self.assertEqual(new_measurement, post_metric_attribute(METRIC_ID, "debt_end_date", self.database))
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            "debt_end_date of metric 'name' of subject 'Subject' in report 'Report' from '' to '2019-06-07'",
            report=updated_report,
        )

    def test_post_unsafe_comment(self, request):
        """Test that comments are sanitized, since they are displayed as inner HTML in the frontend."""
        request.json = dict(comment='Comment with script<script type="text/javascript">alert("Danger")</script>')
        self.assertEqual(dict(ok=True), post_metric_attribute(METRIC_ID, "comment", self.database))
        self.database.reports.insert_one.assert_called_once_with(self.report)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            "comment of metric 'name' of subject 'Subject' in report 'Report' from '' to 'Comment with script'",
            report=updated_report,
        )

    def test_post_comment_with_link(self, request):
        """Test that urls in comments are transformed into anchors."""
        request.json = dict(comment="Comment with url https://google.com")
        self.assertEqual(dict(ok=True), post_metric_attribute(METRIC_ID, "comment", self.database))
        self.database.reports.insert_one.assert_called_once_with(self.report)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            """comment of metric 'name' of subject 'Subject' in report 'Report' from '' to '<p>Comment with url """
            """<a href="https://google.com" target="_blank">https://google.com</a></p>'""",
            report=updated_report,
        )

    def test_post_position_first(self, request):
        """Test that a metric can be moved to the top of the list."""
        request.json = dict(position="first")
        self.assertEqual(dict(ok=True), post_metric_attribute(METRIC_ID2, "position", self.database))
        self.database.reports.insert_one.assert_called_once_with(self.report)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assertEqual([METRIC_ID2, METRIC_ID], list(self.report["subjects"][SUBJECT_ID]["metrics"].keys()))
        self.assert_delta(
            "position of metric 'name2' of subject 'Subject' in report 'Report' from '1' to '0'",
            uuids=[REPORT_ID, SUBJECT_ID, METRIC_ID2],
            report=updated_report,
        )

    def test_post_position_last(self, request):
        """Test that a metric can be moved to the bottom of the list."""
        request.json = dict(position="last")
        self.assertEqual(dict(ok=True), post_metric_attribute(METRIC_ID, "position", self.database))
        self.database.reports.insert_one.assert_called_once_with(self.report)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assertEqual([METRIC_ID2, METRIC_ID], list(self.report["subjects"][SUBJECT_ID]["metrics"].keys()))
        self.assert_delta(
            "position of metric 'name' of subject 'Subject' in report 'Report' from '0' to '1'", report=updated_report
        )

    def test_post_position_previous(self, request):
        """Test that a metric can be moved up."""
        request.json = dict(position="previous")
        self.assertEqual(dict(ok=True), post_metric_attribute(METRIC_ID2, "position", self.database))
        self.database.reports.insert_one.assert_called_once_with(self.report)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assertEqual([METRIC_ID2, METRIC_ID], list(self.report["subjects"][SUBJECT_ID]["metrics"].keys()))
        self.assert_delta(
            "position of metric 'name2' of subject 'Subject' in report 'Report' from '1' to '0'",
            uuids=[REPORT_ID, SUBJECT_ID, METRIC_ID2],
            report=updated_report,
        )

    def test_post_position_next(self, request):
        """Test that a metric can be moved down."""
        request.json = dict(position="next")
        self.assertEqual(dict(ok=True), post_metric_attribute(METRIC_ID, "position", self.database))
        self.database.reports.insert_one.assert_called_once_with(self.report)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assertEqual([METRIC_ID2, METRIC_ID], list(self.report["subjects"][SUBJECT_ID]["metrics"].keys()))
        self.assert_delta(
            "position of metric 'name' of subject 'Subject' in report 'Report' from '0' to '1'", report=updated_report
        )

    def test_post_position_first_previous(self, request):
        """Test that moving the first metric up does nothing."""
        request.json = dict(position="previous")
        self.assertEqual(dict(ok=True), post_metric_attribute(METRIC_ID, "position", self.database))
        self.database.reports.insert_one.assert_not_called()
        self.assertEqual([METRIC_ID, METRIC_ID2], list(self.report["subjects"][SUBJECT_ID]["metrics"].keys()))

    def test_post_position_last_next(self, request):
        """Test that moving the last metric down does nothing."""
        request.json = dict(position="next")
        self.assertEqual(dict(ok=True), post_metric_attribute(METRIC_ID2, "position", self.database))
        self.database.reports.insert_one.assert_not_called()
        self.assertEqual([METRIC_ID, METRIC_ID2], list(self.report["subjects"][SUBJECT_ID]["metrics"].keys()))


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
        self.database.measurements.find_one.return_value = dict(
            _id="id",
            metric_uuid=METRIC_ID,
            count=dict(value="100", status_start="2018-01-01"),
            sources=[],
        )
        request.json = dict(accept_debt=True)
        self.assertDictEqual(
            dict(
                end="2019-01-01",
                sources=[],
                start="2019-01-01",
                metric_uuid=METRIC_ID,
                count=dict(
                    value=None,
                    status=None,
                    status_start="2018-01-01",
                    target="0",
                    near_target="10",
                    debt_target="100",
                    direction="<",
                ),
            ),
            post_metric_debt(METRIC_ID, self.database),
        )
        updated_report = self.database.reports.insert_one.call_args[0][0]
        desired_response_time = Report(self.DATA_MODEL, updated_report).desired_response_time("debt_target_met")
        expected_date = date.today() + timedelta(days=desired_response_time)
        self.assert_delta(
            "accepted debt from 'False' to 'True' and the debt target from 'None' to '100' and the debt end date from "
            f"'None' to '{expected_date.isoformat()}' of metric 'name' of subject 'Subject' in report 'Report'",
            report=updated_report,
        )
        self.assertTrue(updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["accept_debt"])

    def test_turn_metric_technical_debt_on_without_existing_measurement(self, request):
        """Test that accepting technical debt also sets the technical debt value."""
        request.json = dict(accept_debt=True)
        self.assertDictEqual(dict(ok=True), post_metric_debt(METRIC_ID, self.database))
        updated_report = self.database.reports.insert_one.call_args[0][0]
        desired_response_time = Report(self.DATA_MODEL, updated_report).desired_response_time("debt_target_met")
        expected_date = (date.today() + timedelta(days=desired_response_time)).isoformat()
        self.assert_delta(
            f"accepted debt from 'False' to 'True' and the debt end date from 'None' to '{expected_date}' "
            "of metric 'name' of subject 'Subject' in report 'Report'",
            report=updated_report,
        )
        self.assertTrue(updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["accept_debt"])
        self.assertEqual(expected_date, updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["debt_end_date"])

    def test_turn_metric_technical_debt_off_that_is_already_off(self, request):
        """Test that turning debt off when it's already off does nothing."""
        request.json = dict(accept_debt=False)
        self.assertDictEqual(dict(ok=True), post_metric_debt(METRIC_ID, self.database))
        self.database.reports.insert_one.assert_not_called()

    def test_turn_metric_technical_debt_off_that_is_already_off_but_has_debt_target(self, request):
        """Test that turning debt off when it's already off does reset debt target."""
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["debt_target"] = "100"
        request.json = dict(accept_debt=False)
        self.assertDictEqual(dict(ok=True), post_metric_debt(METRIC_ID, self.database))
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            "debt target from '100' to 'None' of metric 'name' of subject 'Subject' in report 'Report'",
            report=updated_report,
        )
        self.assertFalse(updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["accept_debt"])
        self.assertEqual(None, updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["debt_target"])

    def test_turn_metric_technical_debt_off_that_is_already_off_but_has_debt_end_date(self, request):
        """Test that turning debt off when it's already off does reset debt end date."""
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["debt_end_date"] = "2000-01-01"
        request.json = dict(accept_debt=False)
        self.assertDictEqual(dict(ok=True), post_metric_debt(METRIC_ID, self.database))
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            "debt end date from '2000-01-01' to 'None' of metric 'name' of subject 'Subject' in report 'Report'",
            report=updated_report,
        )
        self.assertFalse(updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["accept_debt"])
        self.assertFalse(updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["debt_end_date"])

    def test_turn_metric_technical_debt_off_without_existing_measurement(self, request):
        """Test turning technical debt off."""
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["accept_debt"] = True
        request.json = dict(accept_debt=False)
        self.assertDictEqual(dict(ok=True), post_metric_debt(METRIC_ID, self.database))
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            "accepted debt from 'True' to 'False' of metric 'name' of subject 'Subject' in report 'Report'",
            report=updated_report,
        )
        self.assertFalse(updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["accept_debt"])


class MetricTest(DataModelTestCase):
    """Unit tests for adding and deleting metrics."""

    def setUp(self):
        """Extend to set up the report fixture."""
        super().setUp()
        self.report = Report(self.DATA_MODEL, create_report())
        self.database.reports.find.return_value = [self.report]
        self.database.measurements.find.return_value = []
        self.database.sessions.find_one.return_value = JOHN

    def assert_delta(self, description: str, uuids: list[str] = None, email: str = JOHN["email"], report=None):
        """Assert that the report delta contains the correct data."""
        uuids = sorted(uuids or [REPORT_ID, SUBJECT_ID, METRIC_ID])
        report = report or self.report
        self.assertEqual(dict(uuids=uuids, email=email, description=description), report["delta"])

    @patch("bottle.request")
    def test_add_metric(self, request):
        """Test that a metric can be added."""
        request.json = dict(type="violations")
        self.assertTrue(post_metric_new(SUBJECT_ID, self.database)["ok"])
        updated_report = self.database.reports.insert_one.call_args[0][0]
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
        inserted_metrics = self.database.reports.insert_one.call_args[0][0]["subjects"][SUBJECT_ID]["metrics"]
        updated_report = self.database.reports.insert_one.call_args[0][0]
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
        target_subject = self.report["subjects"][SUBJECT_ID2] = dict(name="Target", metrics={})
        self.assertEqual(dict(ok=True), post_move_metric(METRIC_ID, SUBJECT_ID2, self.database))
        updated_report = self.database.reports.insert_one.call_args[0][0]
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
        target_subject = dict(name="Target", metrics={})
        target_report = dict(
            _id="target_report", title="Target", report_uuid=REPORT_ID2, subjects={SUBJECT_ID2: target_subject}
        )
        self.database.reports.find.return_value = [self.report, target_report]
        self.assertEqual(dict(ok=True), post_move_metric(METRIC_ID, SUBJECT_ID2, self.database))
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
        self.assertEqual(dict(ok=True), delete_metric(METRIC_ID, self.database))
        self.database.reports.insert_one.assert_called_once_with(self.report)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            "John Doe deleted metric 'Metric' from subject 'Subject' in report 'Report'.", report=updated_report
        )


@patch("bottle.request", Mock(json=dict(metric_url="https://quality_time/metric42")))
@patch("model.issue_tracker.requests.post")
class MetricIssueTest(DataModelTestCase):
    """Unit tests for metric issue routes."""

    def setUp(self):
        """Extend to set up the report fixture."""
        super().setUp()
        self.sources = {
            SOURCE_ID: dict(name="Source", type="owasp_zap", parameters=dict(url="https://zap")),
        }
        self.report = Report(
            self.DATA_MODEL,
            dict(
                report_uuid=REPORT_ID,
                issue_tracker=dict(parameters=dict(url="https://tracker", project_key="KEY", issue_type="BUG")),
                subjects={
                    SUBJECT_ID: dict(
                        name="Subject",
                        metrics={METRIC_ID: dict(type="violations", name="name", unit="oopsies", sources=self.sources)},
                    )
                },
            ),
        )
        self.database.reports.find.return_value = [self.report]
        self.database.sessions.find_one.return_value = JOHN
        self.measurement = dict(
            _id="id",
            metric_uuid=METRIC_ID,
            count=dict(status="target_not_met", value="42"),
            sources=[dict(source_uuid=SOURCE_ID, parse_error=None, connection_error=None, value="42")],
        )
        self.database.measurements.find_one.return_value = self.measurement
        self.expected_json = dict(
            fields=dict(
                project=dict(key="KEY"),
                issuetype=dict(name="BUG"),
                summary="Fix 42 oopsies from Source",
                description="The metric [name|https://quality_time/metric42] in Quality-time reports 42 oopsies "
                "from Source.\nPlease go to https://zap for more details.\n",
            )
        )
        self.issue_api = "https://tracker/rest/api/2/issue"
        self.issue_url = "https://tracker/browse/FOO-42"

    def test_add_metric_issue(self, requests_post):
        """Test that an issue can be added to the issue tracker."""
        response = Mock()
        response.json.return_value = dict(key="FOO-42")
        requests_post.return_value = response
        self.assertEqual(dict(ok=True, issue_url=self.issue_url), add_metric_issue(METRIC_ID, self.database))
        requests_post.assert_called_once_with(
            self.issue_api, auth=None, headers={}, json=self.expected_json, timeout=10
        )

    @patch("model.issue_tracker.requests.get")
    def test_add_metric_issue_with_labels(self, requests_get, requests_post):
        """Test that an issue can be added to the issue tracker."""
        self.report["issue_tracker"]["parameters"]["issue_labels"] = ["label", "label with spaces"]
        project_response = Mock()
        project_response.json.return_value = [dict(key="KEY", name="Foo")]
        issue_types_response = Mock()
        issue_types_response.json.return_value = dict(values=[dict(id="1", name="BUG", subtask=False)])
        fields_response = Mock()
        fields_response.json.return_value = dict(values=[dict(fieldId="labels", name="Labels")])
        requests_get.side_effect = [project_response, issue_types_response, fields_response]
        response = Mock()
        response.json.return_value = dict(key="FOO-42")
        requests_post.return_value = response
        self.assertEqual(dict(ok=True, issue_url=self.issue_url), add_metric_issue(METRIC_ID, self.database))
        self.expected_json["fields"]["labels"] = ["label", "label_with_spaces"]
        requests_post.assert_called_once_with(
            self.issue_api, auth=None, headers={}, json=self.expected_json, timeout=10
        )

    @disable_logging
    @patch("model.issue_tracker.requests.get")
    def test_add_metric_issue_with_epic_link(self, requests_get, requests_post):
        """Test that an issue can be added to the issue tracker."""
        self.report["issue_tracker"]["parameters"]["epic_link"] = "FOO-420"
        project_response = Mock()
        project_response.json.return_value = [dict(key="KEY", name="Foo")]
        issue_types_response = Mock()
        issue_types_response.json.return_value = dict(values=[dict(id="1", name="BUG", subtask=False)])
        fields_response = Mock()
        fields_response.json.return_value = dict(values=[dict(fieldId="epic_link_field_id", name="Epic Link")])
        epic_links_response = Mock()
        epic_links_response.json.return_value = dict(
            issues=[dict(key="FOO-420", fields=dict(summary="FOO-420 Summary"))]
        )
        requests_get.side_effect = [project_response, issue_types_response, fields_response, epic_links_response]
        response = Mock()
        response.json.return_value = dict(key="FOO-42")
        requests_post.return_value = response
        self.assertEqual(dict(ok=True, issue_url=self.issue_url), add_metric_issue(METRIC_ID, self.database))
        self.expected_json["fields"]["epic_link_field_id"] = "FOO-420"
        requests_post.assert_called_once_with(
            self.issue_api, auth=None, headers={}, json=self.expected_json, timeout=10
        )

    @disable_logging
    def test_add_metric_issue_failure(self, requests_post):
        """Test that an error message is returned if an issue cannot be added to the issue tracker."""
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError("Oops")
        requests_post.return_value = response
        self.assertEqual(dict(ok=False, error="Oops"), add_metric_issue(METRIC_ID, self.database))

    def test_add_metric_issue_no_measurement(self, _):
        """Test that an error message is returned if an issue is added for a metric without measurements."""
        self.database.measurements.find_one.return_value = None
        self.assertEqual(
            dict(ok=False, error="Can not create an issue for metric without measurements."),
            add_metric_issue(METRIC_ID, self.database),
        )
