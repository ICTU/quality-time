"""Unit tests for the Quality-time notifier."""

import datetime
import unittest
from unittest.mock import patch

from quality_time_notifier import most_recent_measurement_timestamp, notify


class MostRecentMeasurementTimestampTests(unittest.TestCase):
    """Unit tests for the most recent measurement timestamp method."""

    def test_no_measurements(self):
        """Test without measurements."""
        report = dict(subjects=dict(subject1=dict(metrics=dict(metric1=dict(recent_measurements=[])))))
        json = dict(reports=[report])
        self.assertEqual(datetime.datetime.min.isoformat(), most_recent_measurement_timestamp(json))

    def test_one_measurement(self):
        """Test that the end timestamp of the measurement is returned."""
        now = datetime.datetime.now().isoformat()
        report = dict(subjects=dict(subject1=dict(metrics=dict(metric1=dict(recent_measurements=[dict(end=now)])))))
        json = dict(reports=[report])
        self.assertEqual(now, most_recent_measurement_timestamp(json))


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
                now = datetime.datetime.now().isoformat()
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
