"""Unit tests for the collector main script."""

import logging
import unittest
from copy import deepcopy
from datetime import datetime
from unittest.mock import AsyncMock, Mock, call, mock_open, patch

import aiohttp

import quality_time_collector
from base_collectors import Collector, MetricCollector, SourceCollector
from model import SourceMeasurement, SourceResponses


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

        class SourceMetric(SourceCollector):  # pylint: disable=unused-variable # skipcq: PTC-W0065
            """Register a fake collector automatically."""

            async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
                """Override to return a source measurement fixture."""
                return SourceMeasurement(value="42", total="84")

        self.data_model = dict(sources=dict(source=dict(parameters=dict(url=dict(mandatory=True, metrics=["metric"])))))
        self.collector = Collector()
        self.collector.data_model = self.data_model
        self.url = "https://url"
        self.measurement_api_url = "http://localhost:5001/internal-api/v3/measurements"
        self.metrics = dict(
            metric_uuid=dict(
                report_uuid="report_uuid",
                addition="sum",
                type="metric",
                sources=dict(source_id=dict(type="source", parameters=dict(url=self.url))),
            )
        )

    @staticmethod
    def _patched_get(mock_async_get_request, side_effect=None):
        """Return a patched version of aiohttp.ClientSession.get()."""
        mock = AsyncMock(side_effect=side_effect) if side_effect else AsyncMock(return_value=mock_async_get_request)
        if not side_effect:
            mock_async_get_request.close = Mock()
        return patch("aiohttp.ClientSession.get", mock)

    @staticmethod
    def _patched_post(side_effect=None):
        """Return a patched version of aiohttp.ClientSession.post()."""
        post = AsyncMock(side_effect=side_effect)
        post.return_value.close = Mock()
        return patch("aiohttp.ClientSession.post", post)

    async def _fetch_measurements(self, mock_async_get_request, number=1, side_effect=None):
        """Fetch the measurements with patched get method."""
        with self._patched_get(mock_async_get_request, side_effect):
            async with aiohttp.ClientSession() as session:
                for _ in range(number):
                    await self.collector.collect_metrics(session)

    def _source(self, **kwargs):
        """Create a source."""
        connection_error = kwargs.get("connection_error")
        return dict(
            api_url=kwargs.get("api_url", self.url),
            landing_url=kwargs.get("landing_url", self.url),
            value=None if connection_error else kwargs.get("value", "42"),
            total=None if connection_error else kwargs.get("total", "84"),
            entities=[],
            connection_error=connection_error,
            parse_error=None,
            source_uuid="source_id",
        )

    async def test_fetch_successful(self):
        """Test fetching a test metric."""

        class TestMetric(MetricCollector):  # pylint: disable=unused-variable # skipcq: PTC-W0065
            """Register a fake metric collector automatically."""

        class SourceTestMetric(SourceCollector):  # pylint: disable=unused-variable # skipcq: PTC-W0065
            """Register a fake source collector for the test metric automatically."""

            async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
                """Override to return a source measurement fixture."""
                return SourceMeasurement(value="42", total="84")

        metrics = dict(
            metric_uuid=dict(
                report_uuid="report_uuid",
                type="test_metric",
                addition="sum",
                sources=dict(source_id=dict(type="source", parameters=dict(url=self.url))),
            )
        )
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.return_value = metrics
        with self._patched_post() as post:
            await self._fetch_measurements(mock_async_get_request)
        post.assert_called_once_with(
            self.measurement_api_url,
            json=dict(has_error=False, sources=[self._source()], metric_uuid="metric_uuid", report_uuid="report_uuid"),
        )

    async def test_fetch_with_empty_sources(self):
        """Test fetching measurement for a metric with empty sources dict."""
        metrics = dict(metric_uuid=dict(type="metric", addition="sum", sources={}))
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.return_value = metrics
        with self._patched_post() as post:
            await self._fetch_measurements(mock_async_get_request)
        post.assert_not_called()

    async def test_fetch_without_sources(self):
        """Test fetching measurement for a metric without sources."""
        metrics = dict(metric_uuid=dict(type="metric", addition="sum"))
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.return_value = metrics
        with self._patched_post() as post:
            await self._fetch_measurements(mock_async_get_request)
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
        with self._patched_post() as post:
            await self._fetch_measurements(mock_async_get_request)
        post.assert_not_called()

    async def test_fetch_with_get_error(self):
        """Test fetching measurement when getting the metrics fails."""
        with self._patched_post() as post:
            await self._fetch_measurements(Mock(side_effect=RuntimeError))
        post.assert_not_called()

    async def test_fetch_with_client_error(self):
        """Test fetching measurement when getting measurements fails."""
        mock_async_get_request = AsyncMock()
        mock_async_get_request.close = Mock()
        mock_async_get_request.json.return_value = self.metrics
        with self._patched_post() as post:
            await self._fetch_measurements(
                None, side_effect=[mock_async_get_request, aiohttp.ClientConnectionError("error")]
            )
        post.assert_called_once_with(
            self.measurement_api_url,
            json=dict(
                has_error=True,
                sources=[self._source(connection_error="error")],
                metric_uuid="metric_uuid",
                report_uuid="report_uuid",
            ),
        )

    async def test_fetch_with_empty_client_error(self):
        """Test fetching measurement when getting measurements fails with an 'empty' exception.

        This can happen when an exception returns an empty string when converted to string.
        """
        mock_async_get_request = AsyncMock()
        mock_async_get_request.close = Mock()
        mock_async_get_request.json.return_value = self.metrics
        with self._patched_post() as post:
            await self._fetch_measurements(None, side_effect=[mock_async_get_request, aiohttp.ClientPayloadError()])
        post.assert_called_once_with(
            self.measurement_api_url,
            json=dict(
                has_error=True,
                sources=[self._source(connection_error="ClientPayloadError")],
                metric_uuid="metric_uuid",
                report_uuid="report_uuid",
            ),
        )

    async def test_fetch_with_post_error(self):
        """Test fetching measurement when posting fails."""
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.return_value = self.metrics
        with self._patched_post(side_effect=RuntimeError) as post:
            await self._fetch_measurements(mock_async_get_request)
        post.assert_called_once_with(
            self.measurement_api_url,
            json=dict(has_error=False, sources=[self._source()], metric_uuid="metric_uuid", report_uuid="report_uuid"),
        )

    @patch("asyncio.sleep", Mock(side_effect=RuntimeError))
    @patch("builtins.open", mock_open())
    async def test_collect(self):
        """Test the collect method."""
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [self.data_model, self.metrics]
        with self._patched_get(mock_async_get_request), self._patched_post() as post, self.assertRaises(RuntimeError):
            await quality_time_collector.collect()
        post.assert_called_once_with(
            self.measurement_api_url,
            json=dict(has_error=False, sources=[self._source()], metric_uuid="metric_uuid", report_uuid="report_uuid"),
        )

    async def test_fetch_twice(self):
        """Test that the metric is skipped on the second fetch."""
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [self.metrics, self.metrics]
        with self._patched_post() as post:
            await self._fetch_measurements(mock_async_get_request, number=2)
        post.assert_called_once_with(
            self.measurement_api_url,
            json=dict(has_error=False, sources=[self._source()], metric_uuid="metric_uuid", report_uuid="report_uuid"),
        )

    async def test_fetch_in_batches(self):
        """Test that metrics are fetched in batches."""
        self.collector.MEASUREMENT_LIMIT = 1
        self.metrics["metric_uuid2"] = dict(
            report_uuid="report_uuid",
            addition="sum",
            type="metric",
            sources=dict(source_id=dict(type="source", parameters=dict(url=self.url))),
        )
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [self.metrics, self.metrics]
        with self._patched_post() as post:
            await self._fetch_measurements(mock_async_get_request, number=2)
        expected_call1 = call(
            self.measurement_api_url,
            json=dict(has_error=False, sources=[self._source()], metric_uuid="metric_uuid", report_uuid="report_uuid"),
        )
        expected_call2 = call(
            self.measurement_api_url,
            json=dict(has_error=False, sources=[self._source()], metric_uuid="metric_uuid2", report_uuid="report_uuid"),
        )
        post.assert_has_calls(calls=[expected_call1, call().close(), expected_call2, call().close()])

    async def test_prioritize_edited_metrics(self):
        """Test that edited metrics get priority."""
        self.collector.MEASUREMENT_LIMIT = 1
        self.metrics["metric_uuid2"] = dict(
            report_uuid="report_uuid",
            addition="sum",
            type="metric",
            sources=dict(source_id=dict(type="source", parameters=dict(url=self.url))),
        )
        edited_metrics = deepcopy(self.metrics)
        edited_url = edited_metrics["metric_uuid"]["sources"]["source_id"]["parameters"]["url"] = "https://edited_url"
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [self.metrics, edited_metrics]
        with self._patched_post() as post:
            await self._fetch_measurements(mock_async_get_request, number=2)
        expected_call1 = call(
            self.measurement_api_url,
            json=dict(has_error=False, sources=[self._source()], metric_uuid="metric_uuid", report_uuid="report_uuid"),
        )
        expected_call2 = call(
            self.measurement_api_url,
            json=dict(
                has_error=False,
                sources=[self._source(api_url=edited_url, landing_url=edited_url)],
                metric_uuid="metric_uuid",
                report_uuid="report_uuid",
            ),
        )
        post.assert_has_calls(calls=[expected_call1, call().close(), expected_call2, call().close()])

    async def test_missing_mandatory_parameter(self):
        """Test that a metric with sources but without a mandatory parameter is skipped."""
        metrics = dict(
            metric_uuid=dict(
                type="metric", addition="sum", sources=dict(missing=dict(type="source", parameters=dict(url="")))
            )
        )
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.return_value = metrics
        with self._patched_post() as post:
            await self._fetch_measurements(mock_async_get_request)
        post.assert_not_called()

    async def test_missing_mandatory_parameter_with_default_value(self):
        """Test that a metric with sources and a missing mandatory parameter that has a default value is not skipped."""
        self.data_model["sources"]["source"]["parameters"]["token"] = dict(
            default_value="xxx", mandatory=True, metrics=["metric"]
        )
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.return_value = self.metrics
        with self._patched_post() as post:
            await self._fetch_measurements(mock_async_get_request)
        post.assert_called_once_with(
            self.measurement_api_url,
            json=dict(has_error=False, sources=[self._source()], metric_uuid="metric_uuid", report_uuid="report_uuid"),
        )

    @patch("builtins.open", mock_open())
    async def test_fetch_data_model_after_failure(self):
        """Test that the data model is fetched on the second try."""
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [RuntimeError, self.data_model]
        with self._patched_get(mock_async_get_request):
            async with aiohttp.ClientSession() as session:
                self.collector.MAX_SLEEP_DURATION = 0
                data_model = await self.collector.fetch_data_model(session)
        self.assertEqual(self.data_model, data_model)

    @patch("builtins.open", new_callable=mock_open)
    @patch("base_collectors.collector.datetime")
    def test_writing_health_check(self, mocked_datetime, mocked_open):
        """Test that the current time is written to the health check file."""
        mocked_datetime.now.return_value = now = datetime.now()
        self.collector.record_health()
        mocked_open.assert_called_once_with("/home/collector/health_check.txt", "w", encoding="utf-8")
        mocked_open().write.assert_called_once_with(now.isoformat())

    @patch("builtins.open")
    @patch("logging.error")
    def test_fail_writing_health_check(self, mocked_log, mocked_open):
        """Test that a failure to open the health check file is logged, but otherwise ignored."""
        mocked_open.side_effect = io_error = OSError("Some error")
        self.collector.record_health()
        mocked_log.assert_called_once_with(
            "Could not write health check time stamp to %s: %s", "/home/collector/health_check.txt", io_error
        )
