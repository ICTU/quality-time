"""Unit tests for the notification strategies."""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from dateutil.tz import tzutc

from shared.model.measurement import Measurement
from shared.model.metric import Metric

from models.destination import Destination
from models.report import Report
from strategies.notification_strategy import get_metric_status_notifications, get_time_left_notifications

from shared_test_code.fixtures import (
    METRIC_ID,
    METRIC_ID2,
    NOTIFICATION_DESTINATION_ID,
    REPORT_ID,
    REPORT_ID2,
    SUBJECT_ID,
)


class StrategiesTests(unittest.TestCase):
    """Unit tests for the 'number of new red metrics per report' notification strategy."""

    OLD_TIMESTAMP = "2019-01-01T00:00:00+00:00"
    NEW_TIMESTAMP = "2020-01-01T00:00:00+00:00"

    def setUp(self):
        """Override to create a reports JSON fixture."""
        self.most_recent_measurement_seen = datetime.min.replace(tzinfo=tzutc())
        self.red_metric = self.metric(name="metric1", status="target_not_met")
        self.red_metric_measurements = [
            Measurement(
                self.red_metric,
                metric_uuid=METRIC_ID,
                start=self.OLD_TIMESTAMP,
                end=self.NEW_TIMESTAMP,
                count={"status": "target_met", "value": "5"},
            ),
            Measurement(
                self.red_metric,
                metric_uuid=METRIC_ID,
                start=self.NEW_TIMESTAMP,
                end=self.NEW_TIMESTAMP,
                count={"status": "target_not_met", "value": "10"},
            ),
        ]
        self.reports = [
            Report(
                {},
                {
                    "report_uuid": REPORT_ID,
                    "title": "Title",
                    "subjects": {SUBJECT_ID: {"metrics": {METRIC_ID: self.red_metric}, "type": "software"}},
                    "notification_destinations": {
                        "destination_uuid": {
                            "name": "destination",
                            "report_url": "https://report",
                            "webhook": "https://xxxxx.webhook.office.com/xxxxxxxxx",
                        }
                    },
                },
            ),
        ]

    @staticmethod
    def metric(
        name: str = "metric1",
        status: str = "target_met",
        scale: str = "count",
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
                "status_start": status_start or "",
            },
            METRIC_ID,
        )

    def get_metric_status_notifications(self, measurements: list[Measurement] | None = None):
        """Return the notifications."""
        return get_metric_status_notifications(
            self.reports,
            measurements or [],
            self.most_recent_measurement_seen,
        )

    def test_no_reports(self):
        """Test that there is nothing to notify when there are no reports."""
        self.reports = []
        self.assertEqual([], self.get_metric_status_notifications())

    def test_no_red_metrics(self):
        """Test that there is nothing to notify when there are no red metrics."""
        green_metric = self.metric()
        green_metric["recent_measurements"] = [
            Measurement(
                green_metric,
                start=self.OLD_TIMESTAMP,
                end=self.NEW_TIMESTAMP,
                count={"status": "target_met", "value": "0"},
            )
        ]
        self.reports[0]["subjects"][SUBJECT_ID]["metrics"] = {METRIC_ID: green_metric}
        self.assertEqual([], self.get_metric_status_notifications())

    def test_old_red_metric(self):
        """Test that there is nothing to notify if the red metric was already red."""
        self.red_metric_measurements[0]["count"]["status"] = "target_not_met"
        self.assertEqual([], self.get_metric_status_notifications())

    def test_red_metric_without_recent_measurements(self):
        """Test that there is nothing to notify if the red metric has no recent measurements."""
        self.red_metric_measurements = []
        self.assertEqual([], self.get_metric_status_notifications())

    def test_new_red_metric(self):
        """Test that a metric that has become red is included."""
        notifications = self.get_metric_status_notifications(self.red_metric_measurements)
        self.assertEqual(
            ["metric1", "target not met (red)"],
            [notifications[0].metrics[0].metric_name, notifications[0].metrics[0].new_metric_status],
        )

    def test_new_red_metric_without_count_scale(self):
        """Test that a metric that doesn't have a count scale that became red is included."""
        self.assertEqual(
            ["metric1"], [self.get_metric_status_notifications(self.red_metric_measurements)[0].metrics[0].metric_name]
        )

    def test_multiple_reports_with_same_destination(self):
        """Test that the correct metrics are notified when multiple reports notify the same destination."""
        red_metric2 = self.metric(name="metric2", status="target_not_met")
        red_metric2["name"] = "metric2"
        subject2 = {"metrics": {METRIC_ID2: red_metric2}, "type": "software"}
        report2 = {
            "title": "Title",
            "report_uuid": REPORT_ID2,
            "subjects": {SUBJECT_ID: subject2},
            "notification_destinations": {
                NOTIFICATION_DESTINATION_ID: {
                    "report_url": "https://report2",
                    "name": "destination2",
                    "webhook": "https://xxxxx.webhook.office.com/xxxxxxxxx",
                },
            },
        }
        self.reports.append(Report({}, report2))
        red_metric2_measurements = [
            Measurement(
                red_metric2,
                metric_uuid=METRIC_ID2,
                start=self.OLD_TIMESTAMP,
                end=self.NEW_TIMESTAMP,
                count={"status": "target_met", "value": "5"},
            ),
            Measurement(
                red_metric2,
                metric_uuid=METRIC_ID2,
                start=self.NEW_TIMESTAMP,
                end=self.NEW_TIMESTAMP,
                count={"status": "target_not_met", "value": "10"},
            ),
        ]
        red_measurements = self.red_metric_measurements + red_metric2_measurements
        metrics = [notification.metrics for notification in self.get_metric_status_notifications(red_measurements)]
        self.assertEqual(["metric1", "metric2"], [metrics[0][0].metric_name, metrics[1][0].metric_name])

    @patch("logging.getLogger")
    def test_skip_metric_with_invalid_data(self, mocked_get_logger: Mock):
        """Test that metrics with invalid data are skipped and the error is logged."""
        invalid_metric = self.metric(name="metric2", status="debt_target_met")
        invalid_metric["type"] = "non_existing_metric_type"
        self.reports[0]["subjects"][SUBJECT_ID]["metrics"][METRIC_ID2] = invalid_metric
        invalid_metric_measurements = [
            Measurement(
                invalid_metric,
                metric_uuid=METRIC_ID2,
                start=self.OLD_TIMESTAMP,
                end=self.NEW_TIMESTAMP,
                count={"status": "target_met", "value": "5"},
            ),
            Measurement(
                invalid_metric,
                metric_uuid=METRIC_ID2,
                start=self.NEW_TIMESTAMP,
                end=self.NEW_TIMESTAMP,
                count={"status": "debt_target_met", "value": "10"},
            ),
        ]
        notifications = self.get_metric_status_notifications(self.red_metric_measurements + invalid_metric_measurements)
        self.assertEqual(["metric1"], [metric.metric_name for metric in notifications[0].metrics])
        mocked_get_logger.return_value.exception.assert_called_once_with(
            "Skipping metric %s because determining its notification data failed", METRIC_ID2
        )

    def test_no_notification_destinations_configured(self):
        """Test that no notification is to be sent if there are no configurations in notification destinations."""
        self.reports[0]["notification_destinations"] = {}
        self.assertEqual([], self.get_metric_status_notifications())

    def test_notification_destination_without_webhook(self):
        """Test that no notification is to be sent if there are no notification destinations with a webhook."""
        self.reports[0]["notification_destinations"] = {
            "destination_uuid": {"name": "destination", "report_url": "https://report"}
        }
        self.assertEqual([], self.get_metric_status_notifications())

    def test_no_notification_destinations_in_json(self):
        """Test that no notification is to be sent if notification destinations do not exist in the data."""
        del self.reports[0]["notification_destinations"]
        self.assertEqual([], self.get_metric_status_notifications())


class TimeLeftStrategyTests(unittest.TestCase):
    """Unit tests for the 'metrics with a week or less left to address' notification strategy."""

    NOW = datetime(2026, 10, 26, 7, 0, tzinfo=tzutc())

    def setUp(self):
        """Override to create a reports fixture."""
        self.metric = Metric({}, {"name": "metric1", "scale": "count", "type": "tests"}, METRIC_ID)
        self.destination = {"name": "destination", "report_url": "https://report/", "webhook": "https://webhook"}
        self.reports = [
            Report(
                {},
                {
                    "report_uuid": REPORT_ID,
                    "title": "Title",
                    "subjects": {SUBJECT_ID: {"metrics": {METRIC_ID: self.metric}, "type": "software"}},
                    "notification_destinations": {NOTIFICATION_DESTINATION_ID: self.destination},
                },
            ),
        ]

    def measurement(self, status_start: datetime, status: str = "target_not_met") -> Measurement:
        """Create a measurement fixture."""
        timestamp = self.NOW.isoformat()
        scale_measurement = {"status": status, "value": "10", "status_start": status_start.isoformat()}
        return Measurement(self.metric, metric_uuid=METRIC_ID, start=timestamp, end=timestamp, count=scale_measurement)

    def get_time_left_notifications(self, *measurements: Measurement):
        """Return the time left notifications."""
        return get_time_left_notifications(self.reports, list(measurements), self.NOW)

    def test_metric_with_less_than_a_week_left(self):
        """Test that a metric with less than a week left to address it is included."""
        notifications = self.get_time_left_notifications(self.measurement(self.NOW - timedelta(days=1)))
        self.assertEqual(["metric1"], [metric.metric_name for metric in notifications[0].metrics])
        self.assertEqual(Destination("https://webhook", "https://report"), notifications[0].destination)
        self.assertEqual(self.NOW, notifications[0].now)

    def test_overdue_metric(self):
        """Test that a metric that should have been addressed already is included."""
        notifications = self.get_time_left_notifications(self.measurement(self.NOW - timedelta(days=30)))
        self.assertEqual(["metric1"], [metric.metric_name for metric in notifications[0].metrics])

    def test_metric_with_more_than_a_week_left(self):
        """Test that a metric with more than a week left to address it is not included."""
        measurement = self.measurement(self.NOW - timedelta(days=1), status="near_target_met")
        self.assertEqual([], self.get_time_left_notifications(measurement))

    def test_metric_without_deadline(self):
        """Test that a metric without deadline is not included."""
        measurement = self.measurement(self.NOW - timedelta(days=30), status="target_met")
        self.assertEqual([], self.get_time_left_notifications(measurement))

    @patch("logging.getLogger")
    def test_skip_metric_with_invalid_debt_end_date(self, mocked_get_logger: Mock):
        """Test that metrics with an invalid debt end date are skipped and a warning is logged."""
        invalid_metric = Metric(
            {}, {"name": "metric2", "scale": "count", "type": "tests", "debt_end_date": "?"}, METRIC_ID2
        )
        self.reports[0]["subjects"][SUBJECT_ID]["metrics"][METRIC_ID2] = invalid_metric
        timestamp = self.NOW.isoformat()
        scale_measurement = {"status": "debt_target_met", "value": "10", "status_start": timestamp}
        invalid_measurement = Measurement(
            invalid_metric, metric_uuid=METRIC_ID2, start=timestamp, end=timestamp, count=scale_measurement
        )
        notifications = self.get_time_left_notifications(
            self.measurement(self.NOW - timedelta(days=1)), invalid_measurement
        )
        self.assertEqual(["metric1"], [metric.metric_name for metric in notifications[0].metrics])
        mocked_get_logger.return_value.warning.assert_called_once_with(
            "Ignoring invalid debt end date %s of metric %s", "?", METRIC_ID2
        )

    def test_notification_destination_without_webhook(self):
        """Test that no notification is to be sent if there are no notification destinations with a webhook."""
        self.destination["webhook"] = ""
        self.assertEqual([], self.get_time_left_notifications(self.measurement(self.NOW - timedelta(days=1))))
