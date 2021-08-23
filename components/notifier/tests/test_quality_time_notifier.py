"""Unit tests for the Quality-time notifier."""

import unittest
from copy import deepcopy
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, mock_open, patch

from quality_time_notifier import most_recent_measurement_timestamp, notify, record_health, retrieve_data_model

from .data_model import DATA_MODEL


class MostRecentMeasurementTimestampTests(unittest.TestCase):
    """Unit tests for the most recent measurement timestamp method."""

    def test_no_measurements(self):
        """Test without measurements."""
        report = dict(subjects=dict(subject1=dict(metrics=dict(metric1=dict(recent_measurements=[])))))
        json_data = dict(reports=[report])
        self.assertEqual(datetime.min.replace(tzinfo=timezone.utc), most_recent_measurement_timestamp(json_data))

    def test_one_measurement(self):
        """Test that the end timestamp of the measurement is returned."""
        now = datetime.now().replace(microsecond=0, tzinfo=timezone.utc)
        report = dict(
            subjects=dict(subject1=dict(metrics=dict(metric1=dict(recent_measurements=[dict(end=now.isoformat())]))))
        )
        json_data = dict(reports=[report])
        self.assertEqual(now, most_recent_measurement_timestamp(json_data))


class HealthCheckTest(unittest.TestCase):
    """Unit tests for the record_health method."""

    def setUp(self):
        """Set variables required by testcases."""
        self.filename = "/home/notifier/health_check.txt"

    @patch("builtins.open", new_callable=mock_open)
    @patch("quality_time_notifier.datetime")
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


class FakeResponse:
    """Fake response."""

    def __init__(self, json_data):
        self._json = json_data

    def close(self):
        """Mock close method."""

    async def json(self):
        """Return the json from the response."""
        return self._json


@patch("builtins.open", mock_open())
class NotifyTests(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the notify method."""

    def setUp(self):  # pylint: disable=invalid-name
        """Define info that is used in multiple tests."""
        self.url = "https://report1"
        self.title = "Report 1"
        self.history = "2020-01-01T23:59:00+00:00"
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
                        recent_measurements=[
                            dict(start=self.history, end=self.history, count=dict(status="target_met", value="5"))
                        ],
                    )
                ),
            )
        )

    @staticmethod
    async def return_data_model():
        """Retrieve data_model from class variable."""
        return FakeResponse(json_data=DATA_MODEL)

    @staticmethod
    async def return_report(report=None):
        """Return the reports response asynchronously."""
        reports = [report] if report else []
        return FakeResponse(dict(reports=reports))

    @patch("quality_time_notifier.retrieve_data_model", new=AsyncMock())
    @patch("logging.error")
    @patch("asyncio.sleep")
    @patch("aiohttp.ClientSession.get")
    async def test_exception(self, mocked_get, mocked_sleep, mocked_log_error):
        """Test that an exception while retrieving the reports is handled."""
        mocked_get.side_effect = OSError
        mocked_sleep.side_effect = RuntimeError
        try:
            await notify()
        except RuntimeError:
            pass
        mocked_log_error.assert_called_once()

    @patch("pymsteams.connectorcard.send")
    @patch("asyncio.sleep")
    @patch("aiohttp.ClientSession.get")
    async def test_no_new_red_metrics(self, mocked_get, mocked_sleep, mocked_send):
        """Test that no notifications are sent if there are no new red metrics."""
        mocked_get.side_effect = [self.return_data_model(), self.return_report(), self.return_report()]
        mocked_sleep.side_effect = [None, RuntimeError]
        try:
            await notify()
        except RuntimeError:
            pass
        mocked_send.assert_not_called()

    @patch("outbox.Outbox.send_notifications")
    @patch("asyncio.sleep")
    @patch("aiohttp.ClientSession.get")
    async def test_one_new_red_metric(self, mocked_get, mocked_sleep, mocked_outbox):
        """Test that a notification is not sent if there is one new red metric."""
        report = dict(
            report_uuid="report1",
            title=self.title,
            url=self.url,
            notification_destinations=dict(destination1=dict(name="destination name", webhook="www.webhook.com")),
            subjects=self.subjects,
        )
        now = datetime.now().replace(microsecond=0, tzinfo=timezone.utc).isoformat()
        report2 = deepcopy(report)
        report2["subjects"]["subject1"]["metrics"]["metric1"]["recent_measurements"].append(
            dict(start=now, end=now, count=dict(status="target_not_met", value="10"))
        )
        mocked_get.side_effect = [self.return_data_model(), self.return_report(report), self.return_report(report2)]
        mocked_sleep.side_effect = [None, RuntimeError]
        try:
            await notify()
        except RuntimeError:
            pass
        self.assertEqual(mocked_outbox.call_count, 2)

    @patch("pymsteams.connectorcard.send")
    @patch("asyncio.sleep")
    @patch("aiohttp.ClientSession.get")
    async def test_one_old_red_metric_with_one_measurement(self, mocked_get, mocked_sleep, mocked_send):
        """Test that a notification is not sent if there is one old red metric."""
        history = self.history
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
                            recent_measurements=[
                                dict(start=history, end=history, count=dict(status="target_met", value="5"))
                            ],
                        )
                    )
                )
            ),
        )
        mocked_get.side_effect = [self.return_data_model(), self.return_report(report), self.return_report(report)]
        mocked_sleep.side_effect = [None, RuntimeError]
        try:
            await notify()
        except RuntimeError:
            pass
        mocked_send.assert_not_called()

    @patch("logging.error", Mock())
    @patch("asyncio.sleep")
    @patch("logging.warning")
    @patch("aiohttp.ClientSession.get")
    async def test_error_in_get_data_from_api(self, mocked_get, mocked_log_warning, mocked_sleep):
        """Test being unable to retrieve data from the API."""
        mocked_get.side_effect = [Exception]
        mocked_sleep.side_effect = [None, RuntimeError]
        try:
            await retrieve_data_model("v3")
        except RuntimeError:
            pass
        self.assertEqual(2, mocked_log_warning.call_count)

    @patch("pymsteams.connectorcard.send")
    @patch("asyncio.sleep")
    @patch("aiohttp.ClientSession.get")
    async def test_no_webhook_in_notification_destination(self, mocked_get, mocked_sleep, mocked_send):
        """Test that the notifier continues if a destination does not have a webhook configured."""
        report = dict(
            report_uuid="report1",
            title=self.title,
            url=self.url,
            notification_destinations=dict(destination1=dict(name="destination name", webhook="")),
            subjects=self.subjects,
        )
        now = datetime.now().replace(microsecond=0, tzinfo=timezone.utc).isoformat()
        report2 = deepcopy(report)
        report2["subjects"]["subject1"]["metrics"]["metric1"]["recent_measurements"].append(
            dict(start=now, end=now, count=dict(status="target_met", value="10"))
        )
        mocked_get.side_effect = [self.return_data_model(), self.return_report(report), self.return_report(report2)]
        mocked_sleep.side_effect = [None, RuntimeError]
        try:
            await notify()
        except RuntimeError:
            pass
        mocked_send.assert_not_called()
