"""Unit tests for the metric routes."""

import unittest
from unittest.mock import Mock, patch

from routes.metric import (
    delete_metric,
    get_metrics,
    post_metric_attribute,
    post_metric_copy,
    post_metric_new,
    post_move_metric,
)

from ..fixtures import (
    JOHN,
    METRIC_ID,
    METRIC_ID2,
    REPORT_ID,
    REPORT_ID2,
    SOURCE_ID,
    SUBJECT_ID,
    SUBJECT_ID2,
    create_report,
)


@patch("database.reports.iso_timestamp", new=Mock(return_value="2019-01-01T12:00:00+00:00"))
@patch("bottle.request")
class PostMetricAttributeTest(unittest.TestCase):
    """Unit tests for the post metric attribute route."""

    def setUp(self):
        """Override to set up the database."""
        self.report = dict(
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
                            type="old_type",
                            scale="count",
                            addition="sum",
                            direction="<",
                            target="0",
                            near_target="10",
                            debt_target=None,
                            accept_debt=False,
                            tags=[],
                            sources={SOURCE_ID: {}},
                        ),
                        METRIC_ID2: dict(name="name2", type="old_type"),
                    },
                ),
            },
        )
        self.database = Mock()
        self.database.reports.find.return_value = [self.report]
        self.database.measurements.find.return_value = []
        self.database.sessions.find_one.return_value = JOHN
        self.database.datamodels.find_one.return_value = dict(
            _id="id",
            metrics=dict(
                old_type=dict(name="Old type", scales=["count"]),
                new_type=dict(
                    scales=["count"],
                    default_scale="count",
                    addition="sum",
                    direction="<",
                    target="0",
                    near_target="1",
                    tags=[],
                    sources=["source_type"],
                ),
            ),
        )

    @staticmethod
    def set_measurement_id(measurement):
        """Simulate Mongo setting an id on the inserted measurement."""
        measurement["_id"] = "measurement_id"

    def assert_delta(self, description: str, uuids: list[str] = None, email: str = JOHN["email"]):
        """Assert that the report delta contains the correct data."""
        uuids = uuids or [REPORT_ID, SUBJECT_ID, METRIC_ID]
        description = f"John changed the {description}."
        self.assertDictEqual(dict(uuids=uuids, email=email, description=description), self.report["delta"])

    def test_post_metric_name(self, request):
        """Test that the metric name can be changed."""
        request.json = dict(name="ABC")
        self.assertEqual(dict(ok=True), post_metric_attribute(METRIC_ID, "name", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assert_delta("name of metric 'name' of subject 'Subject' in report 'Report' from 'name' to 'ABC'")

    def test_post_metric_type(self, request):
        """Test that the metric type can be changed."""
        request.json = dict(type="new_type")
        self.assertEqual(dict(ok=True), post_metric_attribute(METRIC_ID, "type", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assert_delta("type of metric 'name' of subject 'Subject' in report 'Report' from 'old_type' to 'new_type'")

    def test_post_metric_target_without_measurements(self, request):
        """Test that changing the metric target does not add a new measurement if none exist."""
        self.database.measurements.find_one.return_value = None
        request.json = dict(target="10")
        self.assertEqual(dict(ok=True), post_metric_attribute(METRIC_ID, "target", self.database))
        self.assert_delta("target of metric 'name' of subject 'Subject' in report 'Report' from '0' to '10'")

    @patch("model.measurement.iso_timestamp", new=Mock(return_value="2019-01-01"))
    def test_post_metric_target_with_measurements(self, request):
        """Test that changing the metric target adds a new measurement if one or more exist."""
        self.database.measurements.find_one.return_value = dict(_id="id", metric_uuid=METRIC_ID, sources=[])
        self.database.measurements.insert_one.side_effect = self.set_measurement_id
        request.json = dict(target="10")
        self.assertEqual(
            dict(
                end="2019-01-01",
                sources=[],
                start="2019-01-01",
                metric_uuid=METRIC_ID,
                count=dict(status=None, value=None, target="10", near_target="10", debt_target=None, direction="<"),
            ),
            post_metric_attribute(METRIC_ID, "target", self.database),
        )
        self.assert_delta("target of metric 'name' of subject 'Subject' in report 'Report' from '0' to '10'")

    @patch("model.measurement.iso_timestamp", new=Mock(return_value="2019-01-01"))
    def test_post_metric_technical_debt(self, request):
        """Test that accepting technical debt also sets the technical debt value."""
        self.database.measurements.find_one.return_value = dict(_id="id", metric_uuid=METRIC_ID, sources=[])
        self.database.measurements.insert_one.side_effect = self.set_measurement_id
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
                    target="0",
                    near_target="10",
                    debt_target=None,
                    direction="<",
                ),
            ),
            post_metric_attribute(METRIC_ID, "accept_debt", self.database),
        )
        self.assert_delta("accept_debt of metric 'name' of subject 'Subject' in report 'Report' from '' to 'True'")

    @patch("model.measurement.iso_timestamp", new=Mock(return_value="2019-01-01"))
    def test_post_metric_technical_debt_without_sources(self, request):
        """Test that accepting technical debt when the metric has no sources also sets the status to debt target met."""
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"] = {}
        self.database.measurements.find_one.return_value = dict(_id="id", metric_uuid=METRIC_ID, sources=[])
        self.database.measurements.insert_one.side_effect = self.set_measurement_id
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
        self.assert_delta("accept_debt of metric 'name' of subject 'Subject' in report 'Report' from '' to 'True'")

    @patch("model.measurement.iso_timestamp", new=Mock(return_value="2019-01-01"))
    def test_post_metric_debt_end_date_with_measurements(self, request):
        """Test that changing the metric debt end date adds a new measurement if one or more exist."""
        self.database.measurements.find_one.return_value = dict(_id="id", metric_uuid=METRIC_ID, sources=[])
        self.database.measurements.insert_one.side_effect = self.set_measurement_id
        request.json = dict(debt_end_date="2019-06-07")
        count = dict(value=None, status=None, target="0", near_target="10", debt_target=None, direction="<")
        new_measurement = dict(end="2019-01-01", sources=[], start="2019-01-01", metric_uuid=METRIC_ID, count=count)
        self.assertEqual(new_measurement, post_metric_attribute(METRIC_ID, "debt_end_date", self.database))
        self.assert_delta(
            "debt_end_date of metric 'name' of subject 'Subject' in report 'Report' from '' to '2019-06-07'"
        )

    def test_post_unsafe_comment(self, request):
        """Test that comments are sanitized, since they are displayed as inner HTML in the frontend."""
        request.json = dict(comment='Comment with script<script type="text/javascript">alert("Danger")</script>')
        self.assertEqual(dict(ok=True), post_metric_attribute(METRIC_ID, "comment", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assert_delta(
            "comment of metric 'name' of subject 'Subject' in report 'Report' from '' to 'Comment with script'"
        )

    def test_post_comment_with_link(self, request):
        """Test that urls in comments are transformed into anchors."""
        request.json = dict(comment="Comment with url https://google.com")
        self.assertEqual(dict(ok=True), post_metric_attribute(METRIC_ID, "comment", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assert_delta(
            """comment of metric 'name' of subject 'Subject' in report 'Report' from '' to '<p>Comment with url """
            """<a href="https://google.com">https://google.com</a></p>'"""
        )

    def test_post_position_first(self, request):
        """Test that a metric can be moved to the top of the list."""
        request.json = dict(position="first")
        self.assertEqual(dict(ok=True), post_metric_attribute(METRIC_ID2, "position", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual([METRIC_ID2, METRIC_ID], list(self.report["subjects"][SUBJECT_ID]["metrics"].keys()))
        self.assert_delta(
            "position of metric 'name2' of subject 'Subject' in report 'Report' from '1' to '0'",
            uuids=[REPORT_ID, SUBJECT_ID, METRIC_ID2],
        )

    def test_post_position_last(self, request):
        """Test that a metric can be moved to the bottom of the list."""
        request.json = dict(position="last")
        self.assertEqual(dict(ok=True), post_metric_attribute(METRIC_ID, "position", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual([METRIC_ID2, METRIC_ID], list(self.report["subjects"][SUBJECT_ID]["metrics"].keys()))
        self.assert_delta("position of metric 'name' of subject 'Subject' in report 'Report' from '0' to '1'")

    def test_post_position_previous(self, request):
        """Test that a metric can be moved up."""
        request.json = dict(position="previous")
        self.assertEqual(dict(ok=True), post_metric_attribute(METRIC_ID2, "position", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual([METRIC_ID2, METRIC_ID], list(self.report["subjects"][SUBJECT_ID]["metrics"].keys()))
        self.assert_delta(
            "position of metric 'name2' of subject 'Subject' in report 'Report' from '1' to '0'",
            uuids=[REPORT_ID, SUBJECT_ID, METRIC_ID2],
        )

    def test_post_position_next(self, request):
        """Test that a metric can be moved down."""
        request.json = dict(position="next")
        self.assertEqual(dict(ok=True), post_metric_attribute(METRIC_ID, "position", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual([METRIC_ID2, METRIC_ID], list(self.report["subjects"][SUBJECT_ID]["metrics"].keys()))
        self.assert_delta("position of metric 'name' of subject 'Subject' in report 'Report' from '0' to '1'")

    def test_post_position_first_previous(self, request):
        """Test that moving the first metric up does nothing."""
        request.json = dict(position="previous")
        self.assertEqual(dict(ok=True), post_metric_attribute(METRIC_ID, "position", self.database))
        self.database.reports.insert.assert_not_called()
        self.assertEqual([METRIC_ID, METRIC_ID2], list(self.report["subjects"][SUBJECT_ID]["metrics"].keys()))

    def test_post_position_last_next(self, request):
        """Test that moving the last metric down does nothing."""
        request.json = dict(position="next")
        self.assertEqual(dict(ok=True), post_metric_attribute(METRIC_ID2, "position", self.database))
        self.database.reports.insert.assert_not_called()
        self.assertEqual([METRIC_ID, METRIC_ID2], list(self.report["subjects"][SUBJECT_ID]["metrics"].keys()))


class MetricTest(unittest.TestCase):
    """Unit tests for adding and deleting metrics."""

    def setUp(self):
        """Override to set up the mock database."""
        self.database = Mock()
        self.report = create_report()
        self.database.reports.find.return_value = [self.report]
        self.database.measurements.find.return_value = []
        self.database.sessions.find_one.return_value = JOHN
        self.database.datamodels.find_one.return_value = dict(
            _id="",
            metrics=dict(
                metric_type=dict(
                    name="Metric type",
                    default_scale="count",
                    addition="sum",
                    direction="<",
                    target="0",
                    near_target="1",
                    tags=[],
                )
            ),
            sources=dict(source_type=dict(name="Source type")),
        )

    def assert_delta(self, description: str, uuids: list[str] = None, email: str = JOHN["email"], report=None):
        """Assert that the report delta contains the correct data."""
        uuids = uuids or [REPORT_ID, SUBJECT_ID, METRIC_ID]
        report = report or self.report
        self.assertEqual(dict(uuids=uuids, email=email, description=description), report["delta"])

    def test_add_metric(self):
        """Test that a metric can be added."""
        self.assertTrue(post_metric_new(SUBJECT_ID, self.database)["ok"])
        self.assert_delta(
            "John added a new metric to subject 'Subject' in report 'Report'.",
            uuids=[REPORT_ID, SUBJECT_ID, list(self.report["subjects"][SUBJECT_ID]["metrics"].keys())[1]],
        )

    def test_copy_metric(self):
        """Test that a metric can be copied."""
        self.assertTrue(post_metric_copy(METRIC_ID, SUBJECT_ID, self.database)["ok"])
        self.database.reports.insert.assert_called_once()
        inserted_metrics = self.database.reports.insert.call_args[0][0]["subjects"][SUBJECT_ID]["metrics"]
        self.assertEqual(2, len(inserted_metrics))
        self.assert_delta(
            "John copied the metric 'Metric' of subject 'Subject' from report 'Report' to subject 'Subject' in report "
            "'Report'.",
            uuids=[REPORT_ID, SUBJECT_ID, list(inserted_metrics.keys())[1]],
        )

    def test_move_metric_within_report(self):
        """Test that a metric can be moved to a different subject in the same report."""
        metric = self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]
        target_subject = self.report["subjects"][SUBJECT_ID2] = dict(name="Target", metrics={})
        self.assertEqual(dict(ok=True), post_move_metric(METRIC_ID, SUBJECT_ID2, self.database))
        self.assertEqual({}, self.report["subjects"][SUBJECT_ID]["metrics"])
        self.assertEqual((METRIC_ID, metric), next(iter(target_subject["metrics"].items())))  # noqa: PTC-W0063
        self.assert_delta(
            "John moved the metric 'Metric' from subject 'Subject' in report 'Report' to subject 'Target' in report "
            "'Report'.",
            uuids=[REPORT_ID, SUBJECT_ID, SUBJECT_ID2, METRIC_ID],
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
        self.assertEqual({}, self.report["subjects"][SUBJECT_ID]["metrics"])
        self.assertEqual((METRIC_ID, metric), next(iter(target_subject["metrics"].items())))  # noqa: PTC-W0063
        expected_description = (
            "John moved the metric 'Metric' from subject 'Subject' in report 'Report' to subject 'Target' in report "
            "'Target'."
        )
        self.assert_delta(expected_description)
        self.assert_delta(expected_description, uuids=[REPORT_ID2, SUBJECT_ID2, METRIC_ID], report=target_report)

    def test_get_metrics(self):
        """Test that the metrics can be retrieved and deleted reports are skipped."""
        self.database.reports_overviews.find_one.return_value = dict(_id="id", title="Reports", subtitle="")
        self.database.reports.distinct.return_value = [REPORT_ID, "deleted_report"]
        self.database.reports.find_one.side_effect = [self.report, dict(deleted=True)]
        self.assertEqual(
            {
                METRIC_ID: dict(
                    report_uuid=REPORT_ID,
                    name="Metric",
                    addition="sum",
                    accept_debt=False,
                    type="metric_type",
                    tags=["security"],
                    target="0",
                    sources=dict(
                        source_uuid=dict(
                            name="Source", type="source_type", parameters=dict(url="https://url", password="password")
                        )
                    ),
                )
            },
            get_metrics(self.database),
        )

    def test_delete_metric(self):
        """Test that the metric can be deleted."""
        self.assertEqual(dict(ok=True), delete_metric(METRIC_ID, self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assert_delta("John deleted metric 'Metric' from subject 'Subject' in report 'Report'.")
