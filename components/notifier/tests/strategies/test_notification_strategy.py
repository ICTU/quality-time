"""Unit tests for the notification strategies."""

import unittest
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from shared.model.metric import Metric
from shared.model.report import Report

from strategies.notification_strategy import NotificationFinder

from tests.fixtures import METRIC_ID, METRIC_ID2, NOTIFICATION_DESTINATION_ID, REPORT_ID, REPORT_ID2, SUBJECT_ID

if TYPE_CHECKING:
    from shared.model.measurement import Measurement


class StrategiesTests(unittest.TestCase):
    """Unit tests for the 'number of new red metrics per report' notification strategy."""

    OLD_TIMESTAMP = "2019-01-01T00:00:00+00:00"
    NEW_TIMESTAMP = "2020-01-01T00:00:00+00:00"

    def setUp(self):
        """Override to create a reports JSON fixture."""
        self.notification_finder = NotificationFinder()
        self.most_recent_measurement_seen = datetime.min.replace(tzinfo=UTC)
        self.white_metric_status = "unknown"
        self.red_metric = self.metric(name="metric1", status="target_not_met")
        self.red_metric_measurements = [
            {
                "metric_uuid": METRIC_ID,
                "start": self.OLD_TIMESTAMP,
                "end": self.NEW_TIMESTAMP,
                "count": {"status": "target_met", "value": "5"},
            },
            {
                "metric_uuid": METRIC_ID,
                "start": self.NEW_TIMESTAMP,
                "end": self.NEW_TIMESTAMP,
                "count": {"status": "target_not_met", "value": "10"},
            },
        ]
        self.reports = [
            {
                "report_uuid": REPORT_ID,
                "title": "Title",
                "subjects": {SUBJECT_ID: {"metrics": {METRIC_ID: self.red_metric}, "type": "software"}},
                "notification_destinations": {
                    "destination_uuid": {"name": "destination", "report_url": "https://report"}
                },
            },
        ]

    @staticmethod
    def metric(
        name: str = "metric1",
        status: str = "target_met",
        scale: str = "count",
        recent_measurements: list[Measurement] | None = None,
        status_start: str | None = None,
    ) -> Metric:
        """Create a metric."""
        return Metric(
            {},
            {
                "name": name,
                "scale": scale,
                "status": status,
                "type": "tests",
                "unit": "units",
                "recent_measurements": recent_measurements or [],
                "status_start": status_start or "",
            },
            METRIC_ID,
        )

    def get_notifications(self, measurements: list[Measurement] | None = None):
        """Return the notifications."""
        return self.notification_finder.get_notifications(
            self.reports,
            measurements or [],
            self.most_recent_measurement_seen,
        )

    def test_no_reports(self):
        """Test that there is nothing to notify when there are no reports."""
        self.reports = []
        self.assertEqual([], self.get_notifications())

    def test_no_red_metrics(self):
        """Test that there is nothing to notify when there are no red metrics."""
        green_metric = self.metric(
            recent_measurements=[
                {
                    "start": self.OLD_TIMESTAMP,
                    "end": self.NEW_TIMESTAMP,
                    "count": {"status": "target_met", "value": "0"},
                },
            ],
        )
        self.reports[0]["subjects"][SUBJECT_ID]["metrics"] = {METRIC_ID: green_metric}
        self.assertEqual([], self.get_notifications())

    def test_old_red_metric(self):
        """Test that there is nothing to notify if the red metric was already red."""
        self.red_metric_measurements[0]["count"]["status"] = "target_not_met"
        self.assertEqual([], self.get_notifications())

    def test_red_metric_without_recent_measurements(self):
        """Test that there is nothing to notify if the red metric has no recent measurements."""
        self.red_metric_measurements = []
        self.assertEqual([], self.get_notifications())

    def test_new_red_metric(self):
        """Test that a metric that has become red is included."""
        notifications = self.get_notifications(self.red_metric_measurements)
        self.assertEqual(
            ["metric1", "target not met (red)"],
            [notifications[0].metrics[0].metric_name, notifications[0].metrics[0].new_metric_status],
        )

    def test_new_red_metric_without_count_scale(self):
        """Test that a metric that doesn't have a count scale that became red is included."""
        self.assertEqual(["metric1"], [self.get_notifications(self.red_metric_measurements)[0].metrics[0].metric_name])

    def test_recently_changed_metric_status(self):
        """Test that a metric that turns white is added."""
        metric = self.metric(status=self.white_metric_status)
        measurements = [
            {
                "metric_uuid": METRIC_ID,
                "start": self.NEW_TIMESTAMP,
                "end": self.NEW_TIMESTAMP,
                "count": {"status": "target_met"},
            },
            {
                "metric_uuid": METRIC_ID,
                "start": self.OLD_TIMESTAMP,
                "end": self.OLD_TIMESTAMP,
                "count": {"status": self.white_metric_status},
            },
        ]
        self.assertTrue(
            self.notification_finder.status_changed(metric, measurements, self.most_recent_measurement_seen),
        )

    def test_new_measurement_same_status(self):
        """Test that a metric that was already white isn't added."""
        metric = self.metric(status=self.white_metric_status)
        measurements = [
            {"start": self.NEW_TIMESTAMP, "count": {"status": self.white_metric_status}},
            {"start": self.OLD_TIMESTAMP, "count": {"status": self.white_metric_status}},
        ]
        self.assertFalse(
            self.notification_finder.status_changed(metric, measurements, self.most_recent_measurement_seen),
        )

    def test_no_change_due_to_only_one_measurement(self):
        """Test that metrics with only one measurement (and therefore no changes in value) aren't added."""
        metric = self.metric(status=self.white_metric_status)
        self.assertFalse(self.notification_finder.status_changed(metric, [{}], self.most_recent_measurement_seen))

    def test_no_change_due_to_no_measurements(self):
        """Test that metrics without measurements (and therefore no changes in value) aren't added."""
        metric = self.metric(status=self.white_metric_status)
        self.assertFalse(self.notification_finder.status_changed(metric, [], self.most_recent_measurement_seen))

    def test_multiple_reports_with_same_destination(self):
        """Test that the correct metrics are notified when multiple reports notify the same destination."""
        red_metric2 = self.red_metric.copy()
        red_metric2["name"] = "metric2"
        subject2 = {"metrics": {METRIC_ID2: red_metric2}, "type": "software"}
        report2 = {
            "title": "Title",
            "report_uuid": REPORT_ID2,
            "webhook": "webhook",
            "subjects": {SUBJECT_ID: subject2},
            "notification_destinations": {
                NOTIFICATION_DESTINATION_ID: {"report_url": "https://report2", "name": "destination2"},
            },
        }
        self.reports.append(Report({}, report2))
        red_metric2_measurements = [
            {
                "metric_uuid": METRIC_ID2,
                "start": self.OLD_TIMESTAMP,
                "end": self.NEW_TIMESTAMP,
                "count": {"status": "target_met", "value": "5"},
            },
            {
                "metric_uuid": METRIC_ID2,
                "start": self.NEW_TIMESTAMP,
                "end": self.NEW_TIMESTAMP,
                "count": {"status": "target_not_met", "value": "10"},
            },
        ]
        red_measurements = self.red_metric_measurements + red_metric2_measurements
        metrics = [notification.metrics for notification in self.get_notifications(red_measurements)]
        self.assertEqual(["metric1", "metric2"], [metrics[0][0].metric_name, metrics[1][0].metric_name])

    def test_no_notification_destinations_configured(self):
        """Test that no notification is to be sent if there are no configurations in notification destinations."""
        self.reports[0]["notification_destinations"] = {}
        self.assertEqual([], self.get_notifications())

    def test_no_notification_destinations_in_json(self):
        """Test that no notification is to be sent if notification destinations do not exist in the data."""
        del self.reports[0]["notification_destinations"]
        self.assertEqual([], self.get_notifications())
