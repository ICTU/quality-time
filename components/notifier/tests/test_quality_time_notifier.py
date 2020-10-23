"""Unit tests for the Quality-time notifier."""

import unittest
from datetime import datetime
from unittest.mock import mock_open, patch

from quality_time_notifier import most_recent_measurement_timestamp, notify, record_health


class MostRecentMeasurementTimestampTests(unittest.TestCase):
    """Unit tests for the most recent measurement timestamp method."""

    def test_no_measurements(self):
        """Test without measurements."""
        report = dict(subjects=dict(subject1=dict(metrics=dict(metric1=dict(recent_measurements=[])))))
        json = dict(reports=[report])
        self.assertEqual(datetime.min.isoformat(), most_recent_measurement_timestamp(json))

    def test_one_measurement(self):
        """Test that the end timestamp of the measurement is returned."""
        now = datetime.now().isoformat()
        report = dict(subjects=dict(subject1=dict(metrics=dict(metric1=dict(recent_measurements=[dict(end=now)])))))
        json = dict(reports=[report])
        self.assertEqual(now, most_recent_measurement_timestamp(json))


class HealthCheckTest(unittest.TestCase):
    """Unit tests for the record_health method."""

    def setUp(self):
        self.filename = "/tmp/health_check.txt"

    @patch("builtins.open", new_callable=mock_open)
    @patch("quality_time_notifier.datetime")
    def test_writing_health_check(self, mocked_datetime, mocked_open):
        """Test that the current time is written to the health check file."""
        mocked_datetime.now.return_value = now = datetime.now()
        record_health()
        mocked_open.assert_called_once_with(self.filename, "w")
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

    @patch('pymsteams.connectorcard.send')
    @patch("asyncio.sleep")
    @patch("aiohttp.ClientSession.get")
    async def test_no_new_reds(self, mocked_get, mocked_sleep, mocked_send):
        """Test that no notifications are sent if there are no new red metrics."""

        class Response:  # pylint: disable=too-few-public-methods
            """Fake response."""
            @staticmethod
            async def json():
                """Return the json from the response."""
                return dict(reports=[])

        async def return_response():
            """Return the response asynchronously."""
            return Response()

        mocked_get.return_value = return_response()
        mocked_sleep.side_effect = RuntimeError
        try:
            await notify()
        except RuntimeError:
            pass
        mocked_send.assert_not_called()

    @patch('pymsteams.connectorcard.send')
    @patch("asyncio.sleep")
    @patch("aiohttp.ClientSession.get")
    async def test_one_new_reds(self, mocked_get, mocked_sleep, mocked_send):
        """Test that a notifications is sent if there is one new red metric."""

        class Response:  # pylint: disable=too-few-public-methods
            """Fake response."""
            @staticmethod
            async def json():
                """Return the json from the response."""
                now = datetime.now().isoformat()
                report = dict(
                    report_uuid="report1", title="Report 1", url="http://report1", teams_webhook="http://webhook",
                    subjects=dict(
                        subject1=dict(
                            metrics=dict(
                                metric1=dict(
                                    status="target_not_met", recent_measurements=[dict(start=now, end=now)])))))
                return dict(reports=[report])

        async def return_response():
            """Return the response asynchronously."""
            return Response()

        mocked_get.side_effect = [return_response(), return_response()]
        mocked_sleep.side_effect = [None, RuntimeError]
        try:
            await notify()
        except RuntimeError:
            pass
        mocked_send.assert_called_once()
