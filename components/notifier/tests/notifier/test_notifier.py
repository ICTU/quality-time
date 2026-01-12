"""Unit tests for the Quality-time notifier."""

import contextlib
import pathlib
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, mock_open, patch

import mongomock
from dateutil.tz import tzutc

from shared.model.report import Report

from notifier.notifier import most_recent_measurement_timestamp, notify, record_health

from tests.fixtures import METRIC_ID, METRIC_ID2, NOTIFICATION_DESTINATION_ID, REPORT_ID, SUBJECT_ID, create_report_data


class MostRecentMeasurementTimestampTests(unittest.TestCase):
    """Unit tests for the most recent measurement timestamp method."""

    def test_no_measurements(self):
        """Test without measurements."""
        self.assertEqual(datetime.min.replace(tzinfo=tzutc()), most_recent_measurement_timestamp([]))

    def test_one_measurement(self):
        """Test that the end timestamp of the measurement is returned."""
        now = datetime.now(tz=tzutc()).replace(microsecond=0)
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
        mocked_datetime.now.return_value = now = datetime.now(tz=tzutc())
        record_health()
        mocked_open.assert_called_once_with("w", encoding="utf-8")
        mocked_open().write.assert_called_once_with(now.isoformat())

    @patch("pathlib.Path.open")
    @patch("logging.getLogger")
    def test_fail_writing_health_check(self, mocked_get_logger: Mock, mocked_open: Mock):
        """Test that a failure to open the health check file is logged, but otherwise ignored."""
        logger = mocked_get_logger.return_value = Mock()
        mocked_open.side_effect = OSError("Some error")
        record_health()
        logger.exception.assert_called_once_with("Could not write health check time stamp to %s", self.filename)


@patch("pathlib.Path.open", mock_open())
class NotifyTests(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the notify method."""

    def setUp(self):
        """Define info that is used in multiple tests."""
        self.title = "Report 1"
        self.history = "2020-01-01T23:59:00+00:00"
        self.url = "www.url.com"
        self.database = mongomock.MongoClient()["quality_time_db"]
        self.subjects = {
            SUBJECT_ID: {
                "type": "software",
                "name": "Subject 1",
                "metrics": {
                    METRIC_ID: {
                        "type": "tests",
                        "name": "metric1",
                        "status": "target_not_met",
                        "scale": "count",
                    },
                },
            },
        }

    @patch("logging.getLogger")
    @patch("asyncio.sleep")
    @patch("notifier.notifier.get_reports_and_measurements")
    async def test_exception(self, mocked_get: Mock, mocked_sleep: Mock, mocked_get_logger: Mock):
        """Test that an exception while retrieving the reports is handled."""
        logger = mocked_get_logger.return_value = Mock()
        mocked_get.side_effect = OSError
        mocked_sleep.side_effect = RuntimeError
        with contextlib.suppress(RuntimeError):
            await notify(self.database)

        logger.exception.assert_called_once()
        self.assertEqual(logger.exception.mock_calls[0].args[0], "Getting reports and measurements failed")

    @patch("pymsteams.connectorcard.send")
    @patch("asyncio.sleep")
    @patch("notifier.notifier.get_reports_and_measurements")
    async def test_no_new_red_metrics(self, mocked_get: Mock, mocked_sleep: Mock, mocked_send: Mock):
        """Test that no notifications are sent if there are no new red metrics."""
        report_data = create_report_data()
        now = datetime.now(tz=tzutc()).replace(microsecond=0).isoformat()
        just_now = (datetime.now(tz=tzutc()).replace(microsecond=0) - timedelta(seconds=10)).isoformat()
        measurements = [
            {"metric_uuid": METRIC_ID2, "end": now, "start": now, "count": {"status": "target_not_met", "value": "10"}},
            {
                "metric_uuid": METRIC_ID2,
                "end": just_now,
                "start": just_now,
                "count": {"status": "target_met", "value": "0"},
            },
        ]
        mocked_get.side_effect = [([Report({}, report_data)], measurements), ([Report({}, report_data)], measurements)]
        mocked_sleep.side_effect = [None, RuntimeError]
        with contextlib.suppress(RuntimeError):
            await notify(self.database)

        mocked_send.assert_not_called()

    @patch("notifier.notifier.send_notification")
    @patch("asyncio.sleep")
    @patch("notifier.notifier.get_reports_and_measurements")
    async def test_one_new_red_metric(self, mocked_get: Mock, mocked_sleep: Mock, mocked_send: Mock):
        """Test that a notification is sent if there is one new red metric."""
        report_data = {
            "report_uuid": REPORT_ID,
            "title": self.title,
            "url": self.url,
            "notification_destinations": {
                NOTIFICATION_DESTINATION_ID: {
                    "name": "destination name",
                    "webhook": "www.webhook.com",
                    "report_url": "https://report",
                },
            },
            "subjects": self.subjects,
        }
        now = datetime.now(tz=tzutc()).replace(microsecond=0).isoformat()
        just_now = (datetime.now(tz=tzutc()).replace(microsecond=0) - timedelta(days=1)).isoformat()
        measurements = [
            {"metric_uuid": METRIC_ID, "end": now, "start": now, "count": {"status": "target_not_met", "value": "0"}},
            {
                "metric_uuid": METRIC_ID,
                "end": just_now,
                "start": just_now,
                "count": {"status": "target_met", "value": "10"},
            },
        ]
        mocked_get.side_effect = [([Report({}, report_data)], []), ([Report({}, report_data)], measurements)]

        mocked_sleep.side_effect = [None, RuntimeError]
        with contextlib.suppress(RuntimeError):
            await notify(self.database)

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
            "metric_uuid": METRIC_ID,
            "start": history,
            "end": history,
            "count": {"status": "target_met", "value": "5"},
        }
        report_data = {
            "report_uuid": REPORT_ID,
            "title": self.title,
            "url": self.url,
            "webhook": "https://webhook",
            "subjects": {
                SUBJECT_ID: {
                    "metrics": {
                        METRIC_ID: {
                            "type": "tests",
                            "name": "metric1",
                            "status": "target_not_met",
                            "scale": "count",
                        },
                    },
                },
            },
        }

        mocked_get.return_value = ([Report({}, report_data), Report({}, report_data)], [measurement, measurement])
        mocked_sleep.side_effect = [None, RuntimeError]
        with contextlib.suppress(RuntimeError):
            await notify(self.database)

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
        report_data = create_report_data()
        measurements: list[dict] = []
        mocked_get.side_effect = [([Report({}, report_data)], measurements), ([Report({}, report_data)], measurements)]

        mocked_sleep.side_effect = [None, RuntimeError]
        with contextlib.suppress(RuntimeError):
            await notify(self.database)

        mocked_send.assert_not_called()
