"""Unit tests for the collector main script."""

import logging
import unittest
from datetime import datetime
from unittest.mock import AsyncMock, Mock, mock_open, patch

import aiohttp

import quality_time_collector
from base_collectors import MetricsCollector, SourceCollector
from source_model import SourceMeasurement, SourceResponses


class CollectorTest(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the collection methods."""

    @classmethod
    def setUpClass(cls) -> None:  # pylint: disable=invalid-name
        """Override to disable logging."""
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls) -> None:  # pylint: disable=invalid-name
        """Override to enable logging."""
        logging.disable(logging.NOTSET)

    def setUp(self):  # pylint: disable=invalid-name
        """Override to set up common test data."""

        class SourceMetric(SourceCollector):  # pylint: disable=unused-variable
            """Register a fake collector automatically."""

            async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
                """Override to return a source measurement fixture."""
                return SourceMeasurement(value="42", total="84")

        self.data_model = dict(sources=dict(source=dict(parameters=dict(url=dict(mandatory=True, metrics=["metric"])))))
        self.metrics_collector = MetricsCollector()
        self.metrics_collector.data_model = self.data_model
        self.url = "https://url"
        self.measurement_api_url = "http://localhost:5001/internal-api/v3/measurements"
        self.metrics = dict(
            metric_uuid=dict(
                addition="sum",
                type="metric",
                sources=dict(source_id=dict(type="source", parameters=dict(url=self.url))),
            )
        )

    @staticmethod
    def patched_get(mock_async_get_request, side_effect=None):
        """Return a patched version of aiohttp.ClientSession.get()."""
        mock = AsyncMock(side_effect=side_effect) if side_effect else AsyncMock(return_value=mock_async_get_request)
        if not side_effect:
            mock_async_get_request.close = Mock()
        return patch("aiohttp.ClientSession.get", mock)

    @staticmethod
    def patched_post(side_effect=None):
        """Return a patched version of aiohttp.ClientSession.post()."""
        post = AsyncMock(side_effect=side_effect)
        post.return_value.close = Mock()
        return patch("aiohttp.ClientSession.post", post)

    async def fetch_measurements(self, mock_async_get_request, number=1, side_effect=None):
        """Fetch the measurements with patched get method."""
        with self.patched_get(mock_async_get_request, side_effect):
            async with aiohttp.ClientSession() as session:
                for _ in range(number):
                    await self.metrics_collector.collect_metrics(session)

    async def test_fetch_without_sources(self):
        """Test fetching measurement for a metric without sources."""
        metrics = dict(metric_uuid=dict(type="metric", addition="sum", sources={}))
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.return_value = metrics
        with self.patched_post() as post:
            await self.fetch_measurements(mock_async_get_request)
        post.assert_not_called()

    async def test_fetch_with_unsupported_collector(self):
        """Test fetching measurement for a metric with an unsupported source."""
        metrics = dict(
            metric_uuid=dict(
                type="metric",
                addition="sum",
                sources=dict(source_id=dict(type="unsupported_source", parameters=dict(url=self.url))),
            )
        )
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.return_value = metrics
        with self.patched_post() as post:
            await self.fetch_measurements(mock_async_get_request)
        post.assert_not_called()

    async def test_fetch_with_get_error(self):
        """Test fetching measurement when getting the metrics fails."""
        with self.patched_post() as post:
            await self.fetch_measurements(Mock(side_effect=RuntimeError))
        post.assert_not_called()

    async def test_fetch_with_client_error(self):
        """Test fetching measurement when getting measurements fails."""
        mock_async_get_request = AsyncMock()
        mock_async_get_request.close = Mock()
        mock_async_get_request.json.return_value = self.metrics
        with self.patched_post() as post:
            await self.fetch_measurements(
                None, side_effect=[mock_async_get_request, aiohttp.ClientConnectionError("error")]
            )
        post.assert_called_once_with(
            self.measurement_api_url,
            json=dict(
                sources=[
                    dict(
                        api_url=self.url,
                        landing_url=self.url,
                        value=None,
                        total=None,
                        entities=[],
                        connection_error="error",
                        parse_error=None,
                        source_uuid="source_id",
                    )
                ],
                metric_uuid="metric_uuid",
            ),
        )

    async def test_fetch_with_empty_client_error(self):
        """Test fetching measurement when getting measurements fails with an 'empty' exception.

        This can happen when an exception returns an empty string when converted to string.
        """
        mock_async_get_request = AsyncMock()
        mock_async_get_request.close = Mock()
        mock_async_get_request.json.return_value = self.metrics
        with self.patched_post() as post:
            await self.fetch_measurements(None, side_effect=[mock_async_get_request, aiohttp.ClientPayloadError()])
        post.assert_called_once_with(
            self.measurement_api_url,
            json=dict(
                sources=[
                    dict(
                        api_url=self.url,
                        landing_url=self.url,
                        value=None,
                        total=None,
                        entities=[],
                        connection_error="ClientPayloadError",
                        parse_error=None,
                        source_uuid="source_id",
                    )
                ],
                metric_uuid="metric_uuid",
            ),
        )

    async def test_fetch_with_post_error(self):
        """Test fetching measurement when posting fails."""
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.return_value = self.metrics
        with self.patched_post(side_effect=RuntimeError) as post:
            await self.fetch_measurements(mock_async_get_request)
        post.assert_called_once_with(
            self.measurement_api_url,
            json=dict(
                sources=[
                    dict(
                        api_url=self.url,
                        landing_url=self.url,
                        value="42",
                        total="84",
                        entities=[],
                        connection_error=None,
                        parse_error=None,
                        source_uuid="source_id",
                    )
                ],
                metric_uuid="metric_uuid",
            ),
        )

    @patch("asyncio.sleep", Mock(side_effect=RuntimeError))
    @patch("builtins.open", mock_open())
    async def test_collect(self):
        """Test the collect method."""
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [self.data_model, self.metrics]
        with self.patched_get(mock_async_get_request), self.patched_post() as post, self.assertRaises(RuntimeError):
            await quality_time_collector.collect()
        post.assert_called_once_with(
            self.measurement_api_url,
            json=dict(
                sources=[
                    dict(
                        api_url=self.url,
                        landing_url=self.url,
                        value="42",
                        total="84",
                        entities=[],
                        connection_error=None,
                        parse_error=None,
                        source_uuid="source_id",
                    )
                ],
                metric_uuid="metric_uuid",
            ),
        )

    async def test_fetch_twice(self):
        """Test that the metric is skipped on the second fetch."""
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [self.metrics, self.metrics]
        with self.patched_post() as post:
            await self.fetch_measurements(mock_async_get_request, number=2)
        post.assert_called_once_with(
            self.measurement_api_url,
            json=dict(
                sources=[
                    dict(
                        api_url=self.url,
                        landing_url=self.url,
                        value="42",
                        total="84",
                        entities=[],
                        connection_error=None,
                        parse_error=None,
                        source_uuid="source_id",
                    )
                ],
                metric_uuid="metric_uuid",
            ),
        )

    async def test_missing_mandatory_parameter(self):
        """Test that a metric with sources but without a mandatory parameter is skipped."""
        metrics = dict(
            metric_uuid=dict(
                type="metric", addition="sum", sources=dict(missing=dict(type="source", parameters=dict(url="")))
            )
        )
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.return_value = metrics
        with self.patched_post() as post:
            await self.fetch_measurements(mock_async_get_request)
        post.assert_not_called()

    async def test_missing_mandatory_parameter_with_default_value(self):
        """Test that a metric with sources and a missing mandatory parameter that has a default value is not skipped."""
        self.data_model["sources"]["source"]["parameters"]["token"] = dict(
            default_value="xxx", mandatory=True, metrics=["metric"]
        )
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.return_value = self.metrics
        with self.patched_post() as post:
            await self.fetch_measurements(mock_async_get_request)
        post.assert_called_once_with(
            self.measurement_api_url,
            json=dict(
                sources=[
                    dict(
                        api_url=self.url,
                        landing_url=self.url,
                        value="42",
                        total="84",
                        entities=[],
                        connection_error=None,
                        parse_error=None,
                        source_uuid="source_id",
                    )
                ],
                metric_uuid="metric_uuid",
            ),
        )

    @patch("builtins.open", mock_open())
    async def test_fetch_data_model_after_failure(self):
        """Test that the data model is fetched on the second try."""
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [RuntimeError, self.data_model]
        with self.patched_get(mock_async_get_request):
            async with aiohttp.ClientSession() as session:
                self.metrics_collector.MAX_SLEEP_DURATION = 0
                data_model = await self.metrics_collector.fetch_data_model(session)
        self.assertEqual(self.data_model, data_model)

    @patch("builtins.open", new_callable=mock_open)
    @patch("base_collectors.metrics_collector.datetime")
    def test_writing_health_check(self, mocked_datetime, mocked_open):
        """Test that the current time is written to the health check file."""
        mocked_datetime.now.return_value = now = datetime.now()
        self.metrics_collector.record_health()
        mocked_open.assert_called_once_with("/home/collector/health_check.txt", "w")
        mocked_open().write.assert_called_once_with(now.isoformat())

    @patch("builtins.open")
    @patch("logging.error")
    def test_fail_writing_health_check(self, mocked_log, mocked_open):
        """Test that a failure to open the health check file is logged, but otherwise ignored."""
        mocked_open.side_effect = io_error = OSError("Some error")
        self.metrics_collector.record_health()
        mocked_log.assert_called_once_with(
            "Could not write health check time stamp to %s: %s", "/home/collector/health_check.txt", io_error
        )
