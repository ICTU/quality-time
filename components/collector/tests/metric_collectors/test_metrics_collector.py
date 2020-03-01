"""Unit tests for the collector main script."""

import logging
from datetime import datetime
from typing import Tuple
from unittest.mock import patch, mock_open, AsyncMock, Mock

import aiohttp
import aiounittest

import quality_time_collector
from metric_collectors import MetricsCollector
from source_collectors import source_collector
from collector_utilities.type import Entities, Responses, Value


class CollectorTest(aiounittest.AsyncTestCase):
    """Unit tests for the collection methods."""

    def setUp(self):
        class SourceMetric(source_collector.SourceCollector):  # pylint: disable=unused-variable
            """Register a fake collector automatically."""

            def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
                return "42", "84", []

        self.data_model = dict(sources=dict(source=dict(parameters=dict(url=dict(mandatory=True, metrics=["metric"])))))
        self.metrics_collector = MetricsCollector()
        self.url = "https://url"
        self.measurement_api_url = "http://localhost:5001/api/v2/measurements"
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    @patch("requests.post")
    @patch("aiohttp.ClientSession.get")
    async def test_fetch_without_sources(self, mocked_get, mocked_post):
        """Test fetching measurement for a metric without sources."""
        metrics = dict(metric_uuid=dict(type="metric", addition="sum", sources=dict()))
        response_mock = AsyncMock()
        response_mock.__aenter__.return_value = response_mock
        response_mock.json = AsyncMock(return_value=metrics)
        mocked_get.__aenter__.return_value = mocked_get
        mocked_get.return_value = response_mock
        async with aiohttp.ClientSession() as session:
            await self.metrics_collector.fetch_measurements(session, 60)
        mocked_post.assert_not_called()

    @patch("requests.post")
    @patch("aiohttp.ClientSession.get", Mock(side_effect=RuntimeError))
    async def test_fetch_with_get_error(self, mocked_post):
        """Test fetching measurement when getting fails."""
        async with aiohttp.ClientSession() as session:
            await self.metrics_collector.fetch_measurements(session, 60)
        mocked_post.assert_not_called()

    @patch("requests.get", Mock())
    @patch("requests.post", side_effect=RuntimeError)
    @patch("aiohttp.ClientSession.get")
    async def test_fetch_with_post_error(self, mocked_get, mocked_post):
        """Test fetching measurement when posting fails."""
        metrics = dict(
            metric_uuid=dict(
                addition="sum", type="metric",
                sources=dict(source_id=dict(type="source", parameters=dict(url=self.url)))))
        response_mock = AsyncMock()
        response_mock.__aenter__.return_value = response_mock
        response_mock.json = AsyncMock(return_value=metrics)
        mocked_get.__aenter__.return_value = mocked_get
        mocked_get.return_value = response_mock
        self.metrics_collector.data_model = self.data_model
        async with aiohttp.ClientSession() as session:
            await self.metrics_collector.fetch_measurements(session, 60)
        mocked_post.assert_called_once_with(
            self.measurement_api_url,
            json=dict(
                sources=[
                    dict(api_url=self.url, landing_url=self.url, value="42", total="84", entities=[],
                         connection_error=None, parse_error=None, source_uuid="source_id")],
                metric_uuid="metric_uuid"))

    @patch("asyncio.sleep", Mock(side_effect=RuntimeError))
    @patch("builtins.open", mock_open())
    @patch("requests.get", Mock())
    @patch("requests.post")
    @patch("aiohttp.ClientSession.get")
    async def test_collect(self, mocked_get, mocked_post):
        """Test the collect method."""
        metrics = dict(
            metric_uuid=dict(
                addition="sum", type="metric",
                sources=dict(source_id=dict(type="source", parameters=dict(url=self.url)))))
        response_mock = AsyncMock()
        response_mock.__aenter__.return_value = response_mock
        response_mock.json = AsyncMock(side_effect=[self.data_model, metrics])
        mocked_get.__aenter__.return_value = mocked_get
        mocked_get.return_value = response_mock
        with self.assertRaises(RuntimeError):
            await quality_time_collector.collect()
        mocked_post.assert_called_once_with(
            self.measurement_api_url,
            json=dict(
                sources=[
                    dict(api_url=self.url, landing_url=self.url, value="42", total="84", entities=[],
                         connection_error=None, parse_error=None, source_uuid="source_id")],
                metric_uuid="metric_uuid"))

    @patch("aiohttp.ClientSession.get")
    async def test_missing_collector(self, mocked_get):
        """Test that an exception is thrown if there's no collector for the source and metric type."""
        metrics = dict(
            metric_uuid=dict(
                type="metric", addition="sum",
                sources=dict(missing=dict(type="unknown_source", parameters=dict(url=self.url)))))
        response_mock = AsyncMock()
        response_mock.__aenter__.return_value = response_mock
        response_mock.json = AsyncMock(return_value=metrics)
        mocked_get.__aenter__.return_value = mocked_get
        mocked_get.return_value = response_mock
        with self.assertRaises(LookupError):
            async with aiohttp.ClientSession() as session:
                await self.metrics_collector.fetch_measurements(session, 60)

    @patch("requests.get", Mock())
    @patch("requests.post")
    @patch("aiohttp.ClientSession.get")
    async def test_fetch_twice(self, mocked_get, mocked_post):
        """Test that the metric is skipped on the second fetch."""
        metrics = dict(
            metric_uuid=dict(
                addition="sum", type="metric",
                sources=dict(source_id=dict(type="source", parameters=dict(url=self.url)))))
        response_mock = AsyncMock()
        response_mock.__aenter__.return_value = response_mock
        response_mock.json = AsyncMock(side_effect=[metrics, metrics])
        mocked_get.__aenter__.return_value = mocked_get
        mocked_get.return_value = response_mock
        self.metrics_collector.data_model = self.data_model
        async with aiohttp.ClientSession() as session:
            await self.metrics_collector.fetch_measurements(session, 60)
            await self.metrics_collector.fetch_measurements(session, 60)
        mocked_post.assert_called_once_with(
            "http://localhost:5001/api/v2/measurements",
            json=dict(
                sources=[
                    dict(api_url=self.url, landing_url=self.url, value="42", total="84", entities=[],
                         connection_error=None, parse_error=None, source_uuid="source_id")],
                metric_uuid="metric_uuid"))

    @patch("requests.post")
    @patch("aiohttp.ClientSession.get")
    async def test_missing_mandatory_parameter(self, mocked_get, mocked_post):
        """Test that a metric with sources but without a mandatory parameter is skipped."""
        metrics = dict(
            metric_uuid=dict(
                type="metric", addition="sum", sources=dict(missing=dict(type="source", parameters=dict(url="")))))
        response_mock = AsyncMock()
        response_mock.__aenter__.return_value = response_mock
        response_mock.json = AsyncMock(return_value=metrics)
        mocked_get.__aenter__.return_value = mocked_get
        mocked_get.return_value = response_mock
        self.metrics_collector.data_model = self.data_model
        async with aiohttp.ClientSession() as session:
            await self.metrics_collector.fetch_measurements(session, 60)
        mocked_post.assert_not_called()

    @patch("builtins.open", mock_open())
    @patch("aiohttp.ClientSession.get")
    async def test_fetch_data_model_after_failure(self, mocked_get):
        """Test that the data model is fetched on the second try."""
        response_mock = AsyncMock()
        response_mock.__aenter__.return_value = response_mock
        response_mock.json = AsyncMock(side_effect=[RuntimeError, self.data_model])
        mocked_get.__aenter__.return_value = mocked_get
        mocked_get.return_value = response_mock
        async with aiohttp.ClientSession() as session:
            data_model = await self.metrics_collector.fetch_data_model(session, 0)
        self.assertEqual(self.data_model, data_model)

    @patch("builtins.open", new_callable=mock_open)
    @patch("metric_collectors.metrics_collector.datetime")
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
