"""Unit tests for the Quality-time notifier."""

import json
import pathlib
import unittest
from datetime import datetime
from unittest.mock import AsyncMock, mock_open, Mock, patch

from quality_time_notifier import most_recent_measurement_timestamp, notify, record_health, retrieve_data_model


class MostRecentMeasurementTimestampTests(unittest.TestCase):
    """Unit tests for the most recent measurement timestamp method."""

    def test_no_measurements(self):
        """Test without measurements."""
        report = dict(subjects=dict(subject1=dict(metrics=dict(metric1=dict(recent_measurements=[])))))
        json_data = dict(reports=[report])
        self.assertEqual(datetime.min.isoformat(), most_recent_measurement_timestamp(json_data))

    def test_one_measurement(self):
        """Test that the end timestamp of the measurement is returned."""
        now = datetime.now().isoformat()
        report = dict(subjects=dict(subject1=dict(metrics=dict(metric1=dict(recent_measurements=[dict(end=now)])))))
        json_data = dict(reports=[report])
        self.assertEqual(now, most_recent_measurement_timestamp(json_data))


class HealthCheckTest(unittest.TestCase):
    """Unit tests for the record_health method."""

    def setUp(self):
        """Set variables required by testcases."""
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

    @classmethod
    def setUpClass(cls) -> None:
        """Provide the data_model to the class."""
        module_dir = pathlib.Path(__file__).resolve().parent
        data_model_path = module_dir.parent.parent / "server" / "src" / "data" / "datamodel.json"
        with data_model_path.open() as json_data_model:
            cls.data_model = json.load(json_data_model)

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

    @patch('pymsteams.connectorcard.send')
    @patch("asyncio.sleep")
    @patch("aiohttp.ClientSession.get")
    async def test_no_new_red_metrics(self, mocked_get, mocked_sleep, mocked_send):
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
    async def test_one_new_red_metric(self, mocked_get, mocked_sleep, mocked_send):
        """Test that a notification is sent if there is one new red metric."""
        class Response:
            """Fake response."""

            def __init__(self, json_data=None):
                self._json = json_data
            def close(self):
                """Mock close method."""
            async def json(self):
                """Return the json from the response."""
                if self._json:
                    return self._json
                history = "2020-01-01T00:23:59+59:00" #some data in the past
                now = datetime.now().isoformat()
                report = dict(
                    report_uuid="report1", title="Report 1", url="http://report1", teams_webhook="http://webhook",
                    subjects=dict(
                        subject1=dict(
                            metrics=dict(
                                metric1=dict(
                                    type="tests", name="metric1", unit="units", status="target_not_met",
                                    recent_measurements=[
                                        dict(
                                            start=history,
                                            end=now,
                                            count=dict(status="target_met", value="5")),
                                        dict(
                                            start=now,
                                            end=now,
                                            count=dict(status="target_not_met", value="10"))])))))
                return dict(reports=[report])

        async def return_reports():
            """Return the response asynchronously."""
            return Response()

        async def return_datamodel():
            """Retrieve data_model from class variable."""
            return Response(json_data=self.data_model)

        mocked_get.side_effect = [return_datamodel(), return_reports(), return_reports()]
        mocked_sleep.side_effect = [None, RuntimeError]
        try:
            await notify()
        except RuntimeError:
            pass
        mocked_send.assert_called_once()

    @patch("logging.error", Mock())
    @patch("asyncio.sleep")
    @patch("logging.warning")
    @patch("aiohttp.ClientSession.get")
    async def test_error_in_get_data_from_api(self, mocked_get, mocked_log_warning, mocked_sleep):
        """"Test being unable to retrieve data from api."""
        mocked_get.side_effect = [Exception]
        mocked_sleep.side_effect = [None, RuntimeError]
        try:
            await retrieve_data_model()
        except RuntimeError:
            pass
        self.assertEqual(2, mocked_log_warning.call_count)
