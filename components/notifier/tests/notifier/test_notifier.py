"""Unit tests for the Quality-time notifier."""

import pathlib
import unittest
from copy import deepcopy
from datetime import datetime, timedelta, UTC
from unittest.mock import mock_open, patch, Mock
from tests.fixtures import create_report

from notifier.notifier import most_recent_measurement_timestamp, notify, record_health
import contextlib


class MostRecentMeasurementTimestampTests(unittest.TestCase):
    """Unit tests for the most recent measurement timestamp method."""

    def test_no_measurements(self):
        """Test without measurements."""
        self.assertEqual(datetime.min.replace(tzinfo=UTC), most_recent_measurement_timestamp([]))

    def test_one_measurement(self):
        """Test that the end timestamp of the measurement is returned."""
        now = datetime.now(tz=UTC).replace(microsecond=0)
        measurement = {"end": now.isoformat()}
        self.assertEqual(now, most_recent_measurement_timestamp([measurement]))


class HealthCheckTest(unittest.TestCase):
    """Unit tests for the record_health method."""

    def setUp(self):
        """Set variables required by testcases."""
        self.filename = pathlib.Path("/home/notifier/health_check.txt")

    @patch("pathlib.Path.open", new_callable=mock_open)
    @patch("notifier.notifier.datetime")
    def test_writing_health_check(self, mocked_datetime: Mock, mocked_open: Mock):
        """Test that the current time is written to the health check file."""
        mocked_datetime.now.return_value = now = datetime.now(tz=UTC)
        record_health()
        mocked_open.assert_called_once_with("w", encoding="utf-8")
        mocked_open().write.assert_called_once_with(now.isoformat())

    @patch("pathlib.Path.open")
    @patch("logging.error")
    def test_fail_writing_health_check(self, mocked_log: Mock, mocked_open: Mock):
        """Test that a failure to open the health check file is logged, but otherwise ignored."""
        mocked_open.side_effect = OSError("Some error")
        record_health()
        mocked_log.assert_called_once_with(
            "Could not write health check time stamp to %s",
            self.filename,
            exc_info=True,
        )


@patch("pathlib.Path.open", mock_open())
class NotifyTests(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the notify method."""

    def setUp(self):
        """Define info that is used in multiple tests."""
        self.title = "Report 1"
        self.history = "2020-01-01T23:59:00+00:00"
        self.url = "www.url.com"

        self.subjects = {
            "subject1": {
                "type": "software",
                "name": "Subject 1",
                "metrics": {
                    "metric1": {
                        "type": "tests",
                        "name": "metric1",
                        "unit": "units",
                        "status": "target_not_met",
                        "scale": "count",
                    },
                },
            },
        }

    @patch("logging.error")
    @patch("asyncio.sleep")
    @patch("notifier.notifier.get_reports_and_measurements")
    async def test_exception(self, mocked_get: Mock, mocked_sleep: Mock, mocked_log_error: Mock):
        """Test that an exception while retrieving the reports is handled."""
        mocked_get.side_effect = OSError
        mocked_sleep.side_effect = RuntimeError
        with contextlib.suppress(RuntimeError):
            await notify()

        mocked_log_error.assert_called_once()
        self.assertEqual(mocked_log_error.mock_calls[0].args[0], "Getting reports and measurements failed")

    @patch("pymsteams.connectorcard.send")
    @patch("asyncio.sleep")
    @patch("notifier.notifier.get_reports_and_measurements")
    async def test_no_new_red_metrics(self, mocked_get: Mock, mocked_sleep: Mock, mocked_send: Mock):
        """Test that no notifications are sent if there are no new red metrics."""
        report1 = create_report()
        now = datetime.now(tz=UTC).replace(microsecond=0).isoformat()
        just_now = (datetime.now(tz=UTC).replace(microsecond=0) - timedelta(seconds=10)).isoformat()
        report2 = deepcopy(report1)
        measurements = [
            {"metric_uuid": "metric1", "end": now, "start": now, "count": {"status": "target_not_met", "value": "10"}},
            {
                "metric_uuid": "metric1",
                "end": just_now,
                "start": just_now,
                "count": {"status": "target_met", "value": "0"},
            },
        ]
        mocked_get.side_effect = [([report1], measurements), ([report2], measurements)]
        mocked_sleep.side_effect = [None, RuntimeError]
        with contextlib.suppress(RuntimeError):
            await notify()

        mocked_send.assert_not_called()

    @patch("notifier.notifier.send_notification")
    @patch("asyncio.sleep")
    @patch("notifier.notifier.get_reports_and_measurements")
    async def test_one_new_red_metric(self, mocked_get: Mock, mocked_sleep: Mock, mocked_send: Mock):
        """Test that a notification is sent if there is one new red metric."""
        report1 = {
            "report_uuid": "report1",
            "title": self.title,
            "url": self.url,
            "notification_destinations": {"destination1": {"name": "destination name", "webhook": "www.webhook.com"}},
            "subjects": self.subjects,
        }
        now = datetime.now(tz=UTC).replace(microsecond=0).isoformat()
        just_now = (datetime.now(tz=UTC).replace(microsecond=0) - timedelta(days=1)).isoformat()
        report2 = deepcopy(report1)
        measurements = [
            {"metric_uuid": "metric1", "end": now, "start": now, "count": {"status": "target_not_met", "value": "0"}},
            {
                "metric_uuid": "metric1",
                "end": just_now,
                "start": just_now,
                "count": {"status": "target_met", "value": "10"},
            },
        ]
        mocked_get.side_effect = [([report1], []), ([report2], measurements)]

        mocked_sleep.side_effect = [None, RuntimeError]
        with contextlib.suppress(RuntimeError):
            await notify()

        # gets twice, once for the first report, once for the second
        self.assertEqual(mocked_get.call_count, 2)
        self.assertEqual(mocked_send.call_count, 1)

    @patch("pymsteams.connectorcard.send")
    @patch("asyncio.sleep")
    @patch("notifier.notifier.get_reports_and_measurements")
    async def test_one_old_red_metric_with_one_measurement(
        self,
        mocked_get: Mock,
        mocked_sleep: Mock,
        mocked_send: Mock,
    ):
        """Test that a notification is not sent if there is one old red metric."""
        history = self.history
        measurement = {
            "metric_uuid": "metric1",
            "start": history,
            "end": history,
            "count": {"status": "target_met", "value": "5"},
        }
        report = {
            "report_uuid": "report1",
            "title": self.title,
            "url": self.url,
            "webhook": "https://webhook",
            "subjects": {
                "subject1": {
                    "metrics": {
                        "metric1": {
                            "type": "tests",
                            "name": "metric1",
                            "unit": "units",
                            "status": "target_not_met",
                            "scale": "count",
                        },
                    },
                },
            },
        }

        mocked_get.return_value = ([report, report], [measurement, measurement])
        mocked_sleep.side_effect = [None, RuntimeError]
        with contextlib.suppress(RuntimeError):
            await notify()

        mocked_send.assert_not_called()

    @patch("pymsteams.connectorcard.send")
    @patch("asyncio.sleep")
    @patch("notifier.notifier.get_reports_and_measurements")
    async def test_no_webhook_in_notification_destination(
        self,
        mocked_get: Mock,
        mocked_sleep: Mock,
        mocked_send: Mock,
    ):
        """Test that the notifier continues if a destination does not have a webhook configured."""
        report1 = create_report()
        report2 = deepcopy(report1)
        measurements = []
        mocked_get.side_effect = [([report1], measurements), ([report2], measurements)]

        mocked_sleep.side_effect = [None, RuntimeError]
        with contextlib.suppress(RuntimeError):
            await notify()

        mocked_send.assert_not_called()
