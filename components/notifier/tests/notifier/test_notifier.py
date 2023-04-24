"""Unit tests for the Quality-time notifier."""

import unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from unittest.mock import mock_open, patch
from tests.fixtures import create_report

from notifier.notifier import most_recent_measurement_timestamp, notify, record_health


class MostRecentMeasurementTimestampTests(unittest.TestCase):
    """Unit tests for the most recent measurement timestamp method."""

    def test_no_measurements(self):
        """Test without measurements."""
        self.assertEqual(datetime.min.replace(tzinfo=timezone.utc), most_recent_measurement_timestamp([]))

    def test_one_measurement(self):
        """Test that the end timestamp of the measurement is returned."""
        now = datetime.now().replace(microsecond=0, tzinfo=timezone.utc)
        measurement = dict(end=now.isoformat())
        self.assertEqual(now, most_recent_measurement_timestamp([measurement]))


class HealthCheckTest(unittest.TestCase):
    """Unit tests for the record_health method."""

    def setUp(self):
        """Set variables required by testcases."""
        self.filename = "/home/notifier/health_check.txt"

    @patch("builtins.open", new_callable=mock_open)
    @patch("notifier.notifier.datetime")
    def test_writing_health_check(self, mocked_datetime, mocked_open):
        """Test that the current time is written to the health check file."""
        mocked_datetime.now.return_value = now = datetime.now()
        record_health()
        mocked_open.assert_called_once_with(self.filename, "w", encoding="utf-8")
        mocked_open().write.assert_called_once_with(now.isoformat())

    @patch("builtins.open")
    @patch("logging.error")
    def test_fail_writing_health_check(self, mocked_log, mocked_open):
        """Test that a failure to open the health check file is logged, but otherwise ignored."""
        mocked_open.side_effect = io_error = OSError("Some error")
        record_health()
        mocked_log.assert_called_once_with("Could not write health check time stamp to %s: %s", self.filename, io_error)


@patch("builtins.open", mock_open())
class NotifyTests(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the notify method."""

    def setUp(self):
        """Define info that is used in multiple tests."""
        self.title = "Report 1"
        self.history = "2020-01-01T23:59:00+00:00"
        self.url = "www.url.com"

        self.subjects = dict(
            subject1=dict(
                type="software",
                name="Subject 1",
                metrics=dict(
                    metric1=dict(
                        type="tests",
                        name="metric1",
                        unit="units",
                        status="target_not_met",
                        scale="count",
                    )
                ),
            )
        )

    @patch("logging.error")
    @patch("asyncio.sleep")
    @patch("notifier.notifier.get_reports_and_measurements")
    async def test_exception(self, mocked_get, mocked_sleep, mocked_log_error):
        """Test that an exception while retrieving the reports is handled."""
        mocked_get.side_effect = OSError
        mocked_sleep.side_effect = RuntimeError
        try:
            await notify()
        except RuntimeError:
            pass
        mocked_log_error.assert_called_once()
        self.assertEqual(mocked_log_error.mock_calls[0].args[0], "Getting reports and measurements failed: %s")
        self.assertIsInstance(mocked_log_error.mock_calls[0].args[1], OSError)

    @patch("pymsteams.connectorcard.send")
    @patch("asyncio.sleep")
    @patch("notifier.notifier.get_reports_and_measurements")
    async def test_no_new_red_metrics(self, mocked_get, mocked_sleep, mocked_send):
        """Test that no notifications are sent if there are no new red metrics."""
        report1 = create_report()
        now = datetime.now().replace(microsecond=0, tzinfo=timezone.utc).isoformat()
        just_now = (datetime.now().replace(microsecond=0, tzinfo=timezone.utc) - timedelta(seconds=10)).isoformat()
        report2 = deepcopy(report1)
        measurements = [
            dict(metric_uuid="metric1", end=now, start=now, count=dict(status="target_not_met", value="10")),
            dict(metric_uuid="metric1", end=just_now, start=just_now, count=dict(status="target_met", value="0")),
        ]
        mocked_get.side_effect = [([report1], measurements), ([report2], measurements)]
        mocked_sleep.side_effect = [None, RuntimeError]
        try:
            await notify()
        except RuntimeError:
            pass
        mocked_send.assert_not_called()

    @patch("notifier.notifier.send_notification")
    @patch("asyncio.sleep")
    @patch("notifier.notifier.get_reports_and_measurements")
    async def test_one_new_red_metric(self, mocked_get, mocked_sleep, mocked_send):
        """Test that a notification is sent if there is one new red metric."""
        report1 = dict(
            report_uuid="report1",
            title=self.title,
            url=self.url,
            notification_destinations=dict(destination1=dict(name="destination name", webhook="www.webhook.com")),
            subjects=self.subjects,
        )
        now = datetime.now().replace(microsecond=0, tzinfo=timezone.utc).isoformat()
        just_now = (datetime.now().replace(microsecond=0, tzinfo=timezone.utc) - timedelta(days=1)).isoformat()
        report2 = deepcopy(report1)
        measurements = [
            dict(metric_uuid="metric1", end=now, start=now, count=dict(status="target_not_met", value="0")),
            dict(metric_uuid="metric1", end=just_now, start=just_now, count=dict(status="target_met", value="10")),
        ]
        mocked_get.side_effect = [([report1], []), ([report2], measurements)]

        mocked_sleep.side_effect = [None, RuntimeError]
        try:
            await notify()
        except RuntimeError:
            pass

        # gets twice, once for the first report, once for the second
        self.assertEqual(mocked_get.call_count, 2)
        self.assertEqual(mocked_send.call_count, 1)

    @patch("pymsteams.connectorcard.send")
    @patch("asyncio.sleep")
    @patch("notifier.notifier.get_reports_and_measurements")
    async def test_one_old_red_metric_with_one_measurement(self, mocked_get, mocked_sleep, mocked_send):
        """Test that a notification is not sent if there is one old red metric."""
        history = self.history
        measurement = dict(
            metric_uuid="metric1", start=history, end=history, count=dict(status="target_met", value="5")
        )
        report = dict(
            report_uuid="report1",
            title=self.title,
            url=self.url,
            webhook="https://webhook",
            subjects=dict(
                subject1=dict(
                    metrics=dict(
                        metric1=dict(
                            type="tests",
                            name="metric1",
                            unit="units",
                            status="target_not_met",
                            scale="count",
                        )
                    )
                )
            ),
        )

        mocked_get.return_value = ([report, report], [measurement, measurement])
        mocked_sleep.side_effect = [None, RuntimeError]
        try:
            await notify()
        except RuntimeError:
            pass
        mocked_send.assert_not_called()

    @patch("pymsteams.connectorcard.send")
    @patch("asyncio.sleep")
    @patch("notifier.notifier.get_reports_and_measurements")
    async def test_no_webhook_in_notification_destination(self, mocked_get, mocked_sleep, mocked_send):
        """Test that the notifier continues if a destination does not have a webhook configured."""
        report1 = create_report()
        report2 = deepcopy(report1)
        measurements = []
        mocked_get.side_effect = [([report1], measurements), ([report2], measurements)]

        mocked_sleep.side_effect = [None, RuntimeError]
        try:
            await notify()
        except RuntimeError:
            pass
        mocked_send.assert_not_called()
