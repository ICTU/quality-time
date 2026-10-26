"""Unit tests for the metric notification data model."""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from dateutil.tz import tzlocal, tzutc

from shared.model.metric import Metric
from shared.model.report import Report
from shared.model.subject import Subject

from models.metric_notification_data import MetricNotificationData

from shared_test_code.base import DataModelTestCase
from shared_test_code.fixtures import METRIC_ID, SUBJECT_ID


class MetricNotificationDataModelTestCase(DataModelTestCase):
    """Unit tests for the metric notification data."""

    STATUS_START = "2026-10-01T12:00:00+00:00"

    def metric(self, name: str | None = "default metric 1", unit: str | None = "unit", **kwargs: str) -> Metric:
        """Create a metric fixture."""
        metric_data = {"type": "violations", "scale": "count", **kwargs}
        if name is not None:
            metric_data["name"] = name
        if unit is not None:
            metric_data["unit"] = unit + "s"
            metric_data["unit_singular"] = unit
        return Metric(self.DATA_MODEL, metric_data, METRIC_ID)

    def measurements(self, status: str | None = "target_not_met") -> list:
        """Create measurements fixture."""
        return [
            {"count": {"value": 10, "status": "target_met"}},
            {"count": {"value": 20, "status": status}},
        ]

    def measurements_with_status_start(self, status: str = "target_not_met") -> list:
        """Create measurements fixture with status start."""
        return [{"count": {"value": 20, "status": status, "status_start": self.STATUS_START}}]

    def subject(self, **report_data: dict) -> Subject:
        """Create a subject fixture."""
        report = Report(self.DATA_MODEL, report_data)
        return Subject(self.DATA_MODEL, {"type": "software", "name": "Subject"}, SUBJECT_ID, report)

    def test_new_status(self):
        """Test that the new status is set correctly."""
        notification_data = MetricNotificationData(self.metric(), METRIC_ID, self.measurements(), self.subject())
        self.assertEqual("target_not_met", notification_data.status)
        self.assertEqual("target not met (red)", notification_data.new_metric_status)

    def test_new_status_for_metric_without_unit(self):
        """Test that the new status is set correctly, even if the metric has no unit."""
        notification_data = MetricNotificationData(
            self.metric(unit=None), METRIC_ID, self.measurements(), self.subject()
        )
        self.assertEqual("target_not_met", notification_data.status)
        self.assertEqual("target not met (red)", notification_data.new_metric_status)

    def test_new_status_for_metric_without_name(self):
        """Test that the new status is set correctly, even if the metric has no name."""
        notification_data = MetricNotificationData(
            self.metric(name=None), METRIC_ID, self.measurements(), self.subject()
        )
        self.assertEqual("target_not_met", notification_data.status)
        self.assertEqual("target not met (red)", notification_data.new_metric_status)

    def test_unknown_status(self):
        """Test that a recent measurement without status works."""
        notification_data = MetricNotificationData(self.metric(), METRIC_ID, self.measurements(None), self.subject())
        self.assertEqual("unknown", notification_data.status)
        self.assertEqual("unknown (white)", notification_data.new_metric_status)

    def test_unknown_status_without_recent_measurements(self):
        """Test that a metric without recent measurements works."""
        notification_data = MetricNotificationData(self.metric(), METRIC_ID, [], self.subject())
        self.assertEqual("unknown", notification_data.status)
        self.assertEqual("unknown (white)", notification_data.new_metric_status)

    def test_deadline(self):
        """Test that the deadline is the status start plus the default desired response time."""
        notification_data = MetricNotificationData(
            self.metric(), METRIC_ID, self.measurements_with_status_start(), self.subject()
        )
        self.assertEqual(datetime(2026, 10, 8, 12, 0, tzinfo=tzutc()), notification_data.deadline)

    def test_deadline_with_desired_response_time_of_report(self):
        """Test that the deadline is the status start plus the desired response time of the report."""
        subject = self.subject(desired_response_times={"near_target_met": "10"})
        measurements = self.measurements_with_status_start("near_target_met")
        notification_data = MetricNotificationData(self.metric(), METRIC_ID, measurements, subject)
        self.assertEqual(datetime(2026, 10, 11, 12, 0, tzinfo=tzutc()), notification_data.deadline)

    def test_no_deadline_if_desired_response_time_turned_off(self):
        """Test that the metric has no deadline if the desired response time has been turned off."""
        subject = self.subject(desired_response_times={"target_not_met": None})
        measurements = self.measurements_with_status_start()
        self.assertIsNone(MetricNotificationData(self.metric(), METRIC_ID, measurements, subject).deadline)

    def test_no_deadline_for_status_without_desired_response_time(self):
        """Test that the metric has no deadline if its status has no desired response time."""
        measurements = self.measurements_with_status_start("target_met")
        self.assertIsNone(MetricNotificationData(self.metric(), METRIC_ID, measurements, self.subject()).deadline)

    def test_no_deadline_without_status_start(self):
        """Test that the metric has no deadline if the status start is unknown."""
        measurements = self.measurements()
        self.assertIsNone(MetricNotificationData(self.metric(), METRIC_ID, measurements, self.subject()).deadline)

    def test_no_deadline_without_measurements(self):
        """Test that the metric has no deadline if it has no measurements."""
        self.assertIsNone(MetricNotificationData(self.metric(), METRIC_ID, [], self.subject()).deadline)

    @patch("logging.getLogger")
    def test_no_deadline_with_invalid_debt_end_date(self, mocked_get_logger: Mock):
        """Test that the metric has no deadline if the debt end date is invalid, and that a warning is logged."""
        metric = self.metric(debt_end_date="not a date")
        measurements = self.measurements_with_status_start("debt_target_met")
        self.assertIsNone(MetricNotificationData(metric, METRIC_ID, measurements, self.subject()).deadline)
        mocked_get_logger.return_value.warning.assert_called_once_with(
            "Ignoring invalid debt end date %s of metric %s", "not a date", METRIC_ID
        )

    def test_deadline_for_accepted_technical_debt(self):
        """Test that the deadline of a metric with accepted technical debt is the end of the debt end date."""
        metric = self.metric(debt_end_date="2026-10-31")
        measurements = self.measurements_with_status_start("debt_target_met")
        notification_data = MetricNotificationData(metric, METRIC_ID, measurements, self.subject())
        self.assertEqual(datetime(2026, 10, 31, 23, 59, 59, tzinfo=tzlocal()), notification_data.deadline)

    def test_deadline_for_accepted_technical_debt_with_end_datetime(self):
        """Test that the deadline is the end of the local debt end date if the debt end date is a UTC datetime."""
        local_midnight = datetime(2026, 10, 31, tzinfo=tzlocal())
        metric = self.metric(debt_end_date=local_midnight.astimezone(tzutc()).isoformat())
        measurements = self.measurements_with_status_start("debt_target_met")
        notification_data = MetricNotificationData(metric, METRIC_ID, measurements, self.subject())
        self.assertEqual(datetime(2026, 10, 31, 23, 59, 59, tzinfo=tzlocal()), notification_data.deadline)

    def test_no_deadline_for_accepted_technical_debt_without_end_date(self):
        """Test that a metric with accepted technical debt has no deadline if the debt has no end date."""
        measurements = self.measurements_with_status_start("debt_target_met")
        self.assertIsNone(MetricNotificationData(self.metric(), METRIC_ID, measurements, self.subject()).deadline)

    def test_deadline_on_or_before(self):
        """Test that the deadline is on or before a timestamp if the timestamp is at or after the deadline."""
        notification_data = MetricNotificationData(
            self.metric(), METRIC_ID, self.measurements_with_status_start(), self.subject()
        )
        deadline = datetime(2026, 10, 8, 12, 0, tzinfo=tzutc())
        self.assertTrue(notification_data.deadline_on_or_before(deadline))
        self.assertTrue(notification_data.deadline_on_or_before(deadline + timedelta(seconds=1)))
        self.assertFalse(notification_data.deadline_on_or_before(deadline - timedelta(seconds=1)))

    def test_no_deadline_is_not_on_or_before(self):
        """Test that a metric without deadline does not have a deadline on or before a timestamp."""
        notification_data = MetricNotificationData(self.metric(), METRIC_ID, [], self.subject())
        self.assertFalse(notification_data.deadline_on_or_before(datetime.max.replace(tzinfo=tzutc())))


class MetricNotificationDataStatusChangeTestCase(MetricNotificationDataModelTestCase):
    """Unit tests for determining whether the status of a metric changed."""

    OLD_TIMESTAMP = "2026-10-01T12:00:00+00:00"
    NEW_TIMESTAMP = "2026-10-02T12:00:00+00:00"
    BETWEEN = datetime(2026, 10, 2, tzinfo=tzutc())

    def status_changed_after(self, *statuses: str | None, timestamp: datetime = BETWEEN) -> bool:
        """Return whether the status of a metric with measurements with the statuses changed after the timestamp."""
        starts = (self.OLD_TIMESTAMP, self.NEW_TIMESTAMP)
        measurements: list = [
            {"start": start, "count": {"value": 10, "status": status}}
            for start, status in zip(starts, statuses, strict=False)
        ]
        notification_data = MetricNotificationData(self.metric(), METRIC_ID, measurements, self.subject())
        return notification_data.status_changed_after(timestamp)

    def test_recently_changed_status(self):
        """Test that a metric whose status changed after the timestamp has a changed status."""
        self.assertTrue(self.status_changed_after("target_met", "target_not_met"))

    def test_recently_changed_status_to_unknown(self):
        """Test that a metric that became white after the timestamp has a changed status."""
        self.assertTrue(self.status_changed_after("target_met", None))

    def test_same_status(self):
        """Test that a metric whose status stayed the same does not have a changed status."""
        self.assertFalse(self.status_changed_after("target_not_met", "target_not_met"))

    def test_status_changed_before_timestamp(self):
        """Test that a metric whose status changed before the timestamp does not have a changed status."""
        timestamp = datetime(2026, 10, 3, tzinfo=tzutc())
        self.assertFalse(self.status_changed_after("target_met", "target_not_met", timestamp=timestamp))

    def test_one_measurement(self):
        """Test that a metric with only one measurement does not have a changed status."""
        self.assertFalse(self.status_changed_after("target_not_met"))

    def test_no_measurements(self):
        """Test that a metric without measurements does not have a changed status."""
        self.assertFalse(self.status_changed_after())
