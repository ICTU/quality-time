"""Unit tests for the collector main script."""

import logging
from datetime import datetime
from typing import Tuple
from unittest.mock import patch, mock_open, AsyncMock, Mock

import aiohttp
import aiounittest

import quality_time_collector
from base_collectors import MetricsCollector, SourceCollector
from collector_utilities.type import Entities, Responses, Value


class CollectorTest(aiounittest.AsyncTestCase):
    """Unit tests for the collection methods."""

    @classmethod
    def setUpClass(cls) -> None:
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls) -> None:
        logging.disable(logging.NOTSET)

    def setUp(self):
        class SourceMetric(SourceCollector):  # pylint: disable=unused-variable
            """Register a fake collector automatically."""

            async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
                return "42", "84", []

        self.data_model = dict(sources=dict(source=dict(parameters=dict(url=dict(mandatory=True, metrics=["metric"])))))
        self.metrics_collector = MetricsCollector()
        self.url = "https://url"
        self.measurement_api_url = "http://localhost:5001/api/v2/measurements"

    @staticmethod
    def patched_get(mock_async_get_request, side_effect=None):
        """Return a patched version of aiohttp.ClientSession.get()."""
        mock = AsyncMock(side_effect=side_effect) if side_effect else AsyncMock(return_value=mock_async_get_request)
        if not side_effect:
            mock_async_get_request.close = Mock()
        return patch("aiohttp.ClientSession.get", mock)

    async def fetch_measurements(self, mock_async_get_request, number=1, side_effect=None):
        """Fetch the measurements with patched get method."""
        with self.patched_get(mock_async_get_request, side_effect):
            async with aiohttp.ClientSession() as session:
                for _ in range(number):
                    await self.metrics_collector.collect_metrics(session, 60)

    @patch("aiohttp.ClientSession.post")
    async def test_fetch_without_sources(self, mocked_post):
        """Test fetching measurement for a metric without sources."""
        metrics = dict(metric_uuid=dict(type="metric", addition="sum", sources=dict()))
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.return_value = metrics
        await self.fetch_measurements(mock_async_get_request)
        mocked_post.assert_not_called()

    @patch("aiohttp.ClientSession.post")
    async def test_fetch_with_get_error(self, mocked_post):
        """Test fetching measurement when getting the metrics fails."""
        await self.fetch_measurements(Mock(side_effect=RuntimeError))
        mocked_post.assert_not_called()

    @patch("aiohttp.ClientSession.post")
    async def test_fetch_with_client_error(self, mocked_post):
        """Test fetching measurement when getting measurements fails."""
        metrics = dict(
            metric_uuid=dict(
                addition="sum", type="metric",
                sources=dict(source_id=dict(type="source", parameters=dict(url=self.url)))))
        self.metrics_collector.data_model = self.data_model
        mock_async_get_request = AsyncMock()
        mock_async_get_request.close = Mock()
        mock_async_get_request.json.return_value = metrics
        await self.fetch_measurements(
            None, side_effect=[mock_async_get_request, aiohttp.ClientConnectionError("error")])
        mocked_post.assert_called_once_with(
            self.measurement_api_url,
            json=dict(
                sources=[
                    dict(api_url=self.url, landing_url=self.url, value=None, total=None, entities=[],
                         connection_error="error", parse_error=None, source_uuid="source_id")],
                metric_uuid="metric_uuid"))

    @patch("aiohttp.ClientSession.post", side_effect=RuntimeError)
    async def test_fetch_with_post_error(self, mocked_post):
        """Test fetching measurement when posting fails."""
        metrics = dict(
            metric_uuid=dict(
                addition="sum", type="metric",
                sources=dict(source_id=dict(type="source", parameters=dict(url=self.url)))))
        self.metrics_collector.data_model = self.data_model
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.return_value = metrics
        await self.fetch_measurements(mock_async_get_request)
        mocked_post.assert_called_once_with(
            self.measurement_api_url,
            json=dict(
                sources=[
                    dict(api_url=self.url, landing_url=self.url, value="42", total="84", entities=[],
                         connection_error=None, parse_error=None, source_uuid="source_id")],
                metric_uuid="metric_uuid"))

    @patch("asyncio.sleep", Mock(side_effect=RuntimeError))
    @patch("builtins.open", mock_open())
    async def test_collect(self):
        """Test the collect method."""
        metrics = dict(
            metric_uuid=dict(
                addition="sum", type="metric",
                sources=dict(source_id=dict(type="source", parameters=dict(url=self.url)))))
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [self.data_model, metrics]
        mocked_post = AsyncMock()
        mocked_post.return_value.close = Mock()
        with self.patched_get(mock_async_get_request):
            with patch("aiohttp.ClientSession.post", mocked_post):
                with self.assertRaises(RuntimeError):
                    await quality_time_collector.collect()
        mocked_post.assert_called_once_with(
            self.measurement_api_url,
            json=dict(
                sources=[
                    dict(api_url=self.url, landing_url=self.url, value="42", total="84", entities=[],
                         connection_error=None, parse_error=None, source_uuid="source_id")],
                metric_uuid="metric_uuid"))

    async def test_missing_collector(self):
        """Test that an exception is thrown if there's no collector for the source and metric type."""
        metrics = dict(
            metric_uuid=dict(
                type="metric", addition="sum",
                sources=dict(missing=dict(type="unknown_source", parameters=dict(url=self.url)))))
        self.metrics_collector.data_model = self.data_model
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.return_value = metrics
        with self.assertRaises(LookupError):
            await self.fetch_measurements(mock_async_get_request)

    @patch("aiohttp.ClientSession.post")
    async def test_fetch_twice(self, mocked_post):
        """Test that the metric is skipped on the second fetch."""
        metrics = dict(
            metric_uuid=dict(
                addition="sum", type="metric",
                sources=dict(source_id=dict(type="source", parameters=dict(url=self.url)))))
        self.metrics_collector.data_model = self.data_model
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [metrics, metrics]
        await self.fetch_measurements(mock_async_get_request, number=2)
        mocked_post.assert_called_once_with(
            "http://localhost:5001/api/v2/measurements",
            json=dict(
                sources=[
                    dict(api_url=self.url, landing_url=self.url, value="42", total="84", entities=[],
                         connection_error=None, parse_error=None, source_uuid="source_id")],
                metric_uuid="metric_uuid"))

    @patch("aiohttp.ClientSession.post")
    async def test_missing_mandatory_parameter(self, mocked_post):
        """Test that a metric with sources but without a mandatory parameter is skipped."""
        metrics = dict(
            metric_uuid=dict(
                type="metric", addition="sum", sources=dict(missing=dict(type="source", parameters=dict(url="")))))
        self.metrics_collector.data_model = self.data_model
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.return_value = metrics
        await self.fetch_measurements(mock_async_get_request)
        mocked_post.assert_not_called()

    @patch("builtins.open", mock_open())
    async def test_fetch_data_model_after_failure(self):
        """Test that the data model is fetched on the second try."""
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [RuntimeError, self.data_model]
        with self.patched_get(mock_async_get_request):
            async with aiohttp.ClientSession() as session:
                data_model = await self.metrics_collector.fetch_data_model(session, 0)
        self.assertEqual(self.data_model, data_model)

    @patch("builtins.open", new_callable=mock_open)
    @patch("base_collectors.metrics_collector.datetime")
    def test_writing_health_check(self, mocked_datetime, mocked_open):
        """Test that the current time is written to the health check file."""
        mocked_datetime.now.return_value = now = datetime.now()
        self.metrics_collector.record_health()
        mocked_open.assert_called_once_with("/tmp/health_check.txt", "w")
        mocked_open().write.assert_called_once_with(now.isoformat())

    @patch("builtins.open")
    @patch("logging.error")
    def test_fail_writing_health_check(self, mocked_log, mocked_open):
        """Test that a failure to open the health check file is logged, but otherwise ignored."""
        mocked_open.side_effect = io_error = OSError("Some error")
        self.metrics_collector.record_health()
        mocked_log.assert_called_once_with(
            "Could not write health check time stamp to %s: %s", "/tmp/health_check.txt", io_error)
