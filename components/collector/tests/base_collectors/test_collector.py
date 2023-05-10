"""Unit tests for the collector main script."""

from __future__ import annotations

import logging
import pathlib
import unittest
from datetime import datetime
from unittest.mock import AsyncMock, Mock, call, mock_open, patch

import aiohttp
import mongomock

import quality_time_collector
from base_collectors import Collector
from tests.fixtures import METRIC_ID, METRIC_ID2, SOURCE_ID, SUBJECT_ID, create_report


class CollectorTest(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the collection methods."""

    database_client = "shared.initialization.database.client"
    create_measurement = "base_collectors.collector.create_measurement"

    @classmethod
    def setUpClass(cls) -> None:
        """Override to disable logging."""
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls) -> None:
        """Override to enable logging."""
        logging.disable(logging.NOTSET)

    def setUp(self):
        """Override to set up common test data."""
        self.collector = Collector()
        self.url = "https://url"
        self.metrics = {
            "metric_uuid": {
                "report_uuid": "report_uuid",
                "addition": "sum",
                "type": "dependencies",
                "sources": {"source_uuid": {"type": "pip", "parameters": {"url": self.url}}},
            },
        }
        self.pip_json = [{"name": "a dependency"}]
        self.client = mongomock.MongoClient()
        self.client["quality_time_db"]["reports"].insert_one(create_report())

    @staticmethod
    def _patched_get(mock_async_get_request: AsyncMock, side_effect=None) -> _patch[AsyncMock]:
        """Return a patched version of aiohttp.ClientSession.get()."""
        mock = AsyncMock(side_effect=side_effect) if side_effect else AsyncMock(return_value=mock_async_get_request)
        return patch("aiohttp.ClientSession.get", mock)

    async def _fetch_measurements(self, mock_async_get_request, number=1, side_effect=None):
        """Fetch the measurements with patched get method."""
        with self._patched_get(mock_async_get_request, side_effect):
            async with aiohttp.ClientSession() as session:
                for _ in range(number):
                    await self.collector.collect_metrics(session)

    def _source(self, **kwargs: str | int | float) -> dict[str, str | None | list[dict[str, str]]]:
        """Create a source."""
        connection_error = kwargs.get("connection_error")
        entities = kwargs.get(
            "entities", [dict(name="a dependency", key="a dependency@?", version="unknown", latest="unknown")]
        )
        return {
            "api_url": str(kwargs.get("api_url", self.url)),
            "landing_url": str(kwargs.get("landing_url", self.url)),
            "value": None if connection_error else str(kwargs.get("value", "1")),
            "total": None if connection_error else str(kwargs.get("total", "100")),
            "entities": [] if connection_error else entities,
            "connection_error": connection_error,
            "parse_error": None,
            "source_uuid": "source_id",
        }

    async def test_fetch_successful(self):
        """Test fetching a test metric."""
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [self.pip_json]
        with patch(self.create_measurement) as post, patch(self.database_client, return_value=self.client):
            await self._fetch_measurements(mock_async_get_request)
        post.assert_called_once_with(
            dict(has_error=False, sources=[self._source()], metric_uuid="metric_uuid", report_uuid="report1"),
        )

    async def test_fetch_without_sources(self):
        """Test fetching measurement for a metric without sources."""
        report_with_no_source = create_report()
        report_with_no_source["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"] = dict()
        mock_async_get_request = AsyncMock()
        with patch(self.create_measurement) as post, patch(self.database_client, return_value=self.client):
            self.client["quality_time_db"]["reports"].insert_one(report_with_no_source)
            await self._fetch_measurements(mock_async_get_request)
        post.assert_not_called()

    async def test_fetch_with_unsupported_collector(self):
        """Test fetching measurement for a metric with an unsupported source."""
        report_with_unsupported_source = create_report()
        report_with_unsupported_source["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID] = dict(
            type="unsupported_source"
        )
        mock_async_get_request = AsyncMock()
        with patch(self.create_measurement) as post, patch(self.database_client, return_value=self.client):
            self.client["quality_time_db"]["reports"].insert_one(report_with_unsupported_source)
            await self._fetch_measurements(mock_async_get_request)
        post.assert_not_called()

    async def test_fetch_with_get_error(self):
        """Test fetching measurement when getting the metrics fails."""
        with patch(self.create_measurement) as post, patch(
            self.database_client, return_value=self.client, side_effect=RuntimeError
        ) as _, self.assertRaises(RuntimeError):
            await self._fetch_measurements(AsyncMock())

        post.assert_not_called()

    async def test_fetch_with_client_error(self):
        """Test fetching measurement when getting measurements fails."""
        with patch(self.create_measurement) as post, patch(self.database_client, return_value=self.client):
            await self._fetch_measurements(None, side_effect=[aiohttp.ClientConnectionError("error")])
        post.assert_called_once_with(
            dict(
                has_error=True,
                sources=[self._source(connection_error="error")],
                metric_uuid="metric_uuid",
                report_uuid="report1",
            ),
        )

    async def test_fetch_with_empty_client_error(self):
        """Test fetching measurement when getting measurements fails with an 'empty' exception.

        This can happen when an exception returns an empty string when converted to string.
        """
        with patch(self.create_measurement) as post, patch(self.database_client, return_value=self.client):
            await self._fetch_measurements(None, side_effect=[aiohttp.ClientPayloadError()])
        post.assert_called_once_with(
            dict(
                has_error=True,
                sources=[self._source(connection_error="ClientPayloadError")],
                metric_uuid="metric_uuid",
                report_uuid="report1",
            ),
        )

    async def test_fetch_with_post_error(self):
        """Test fetching measurement when posting fails."""
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [self.pip_json]
        with patch(self.create_measurement) as post, patch(self.database_client, return_value=self.client):
            await self._fetch_measurements(mock_async_get_request)
        post.assert_called_once_with(
            dict(has_error=False, sources=[self._source()], metric_uuid="metric_uuid", report_uuid="report1"),
        )

    @patch("asyncio.sleep", Mock(side_effect=RuntimeError))
    @patch("builtins.open", mock_open())
    async def test_collect(self):
        """Test the collect method."""
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [self.pip_json]
        with patch(self.database_client, return_value=self.client), self._patched_get(mock_async_get_request), patch(
            self.create_measurement
        ) as post, self.assertRaises(RuntimeError):
            await quality_time_collector.collect()
        post.assert_called_once_with(
            dict(has_error=False, sources=[self._source()], metric_uuid="metric_uuid", report_uuid="report1"),
        )

    async def test_fetch_twice(self):
        """Test that the metric is skipped on the second fetch."""
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [self.pip_json, self.pip_json]
        with patch(self.create_measurement) as post, patch(self.database_client, return_value=self.client):
            await self._fetch_measurements(mock_async_get_request, number=2)
        post.assert_called_once_with(
            dict(has_error=False, sources=[self._source()], metric_uuid="metric_uuid", report_uuid="report1"),
        )

    @patch.object(Collector, "MEASUREMENT_LIMIT", 1)
    async def test_fetch_in_batches(self):
        """Test that metrics are fetched in batches."""
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [self.pip_json, self.pip_json]

        with patch(self.create_measurement) as post, patch(self.database_client, return_value=self.client):
            self.client["quality_time_db"]["reports"].insert_one(create_report(metric_id=METRIC_ID2))
            await self._fetch_measurements(mock_async_get_request, number=2)
        expected_call1 = call(
            dict(has_error=False, sources=[self._source()], metric_uuid="metric_uuid", report_uuid="report1"),
        )
        expected_call2 = call(
            dict(has_error=False, sources=[self._source()], metric_uuid="metric_uuid2", report_uuid="report1"),
        )
        post.assert_has_calls(calls=[expected_call1, expected_call2])

    @patch.object(Collector, "MEASUREMENT_LIMIT", 1)
    async def test_prioritize_edited_metrics(self):
        """Test that edited metrics get priority."""
        report1 = create_report()
        report2 = create_report(metric_id=METRIC_ID2)
        edited_url = "https://edited_url"
        report2["subjects"][SUBJECT_ID]["metrics"][METRIC_ID2]["sources"][SOURCE_ID]["parameters"]["url"] = edited_url

        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [self.pip_json, self.pip_json]
        with patch(self.create_measurement) as post, patch(self.database_client, return_value=self.client):
            self.client["quality_time_db"]["reports"].insert_one(report1)
            self.client["quality_time_db"]["reports"].insert_one(report2)
            await self._fetch_measurements(mock_async_get_request, number=2)

        expected_call1 = call(
            dict(has_error=False, sources=[self._source()], metric_uuid="metric_uuid", report_uuid="report1"),
        )
        expected_call2 = call(
            dict(
                has_error=False,
                sources=[self._source(api_url=edited_url, landing_url=edited_url)],
                metric_uuid="metric_uuid2",
                report_uuid="report1",
            ),
        )
        post.assert_has_calls(calls=[expected_call1, expected_call2])

    async def test_missing_mandatory_parameter(self):
        """Test that a metric with sources but without a mandatory parameter is skipped."""
        report_without_url_parameter = create_report()
        report_without_url_parameter["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]["parameters"][
            "url"
        ] = ""
        mock_async_get_request = AsyncMock()
        with patch(self.create_measurement) as post, patch(self.database_client, return_value=self.client):
            self.client["quality_time_db"]["reports"].insert_one(report_without_url_parameter)
            await self._fetch_measurements(mock_async_get_request)
        post.assert_not_called()

    async def test_missing_mandatory_parameter_with_default_value(self):
        """Test that a metric with sources and a missing mandatory parameter that has a default value is not skipped."""
        self.metrics["metric_uuid"]["sources"]["source_id"] = dict(type="manual_number")
        report_without_mandatory_parameter = create_report()
        report_without_mandatory_parameter["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID] = dict(
            type="manual_number"
        )
        mock_async_get_request = AsyncMock()
        with patch(self.create_measurement) as post, patch(self.database_client, return_value=self.client):
            self.client["quality_time_db"]["reports"].insert_one(report_without_mandatory_parameter)
            await self._fetch_measurements(mock_async_get_request)
        post.assert_called_once_with(
            dict(
                has_error=False,
                sources=[self._source(value="0", entities=[], api_url="", landing_url="")],
                metric_uuid="metric_uuid",
                report_uuid="report1",
            ),
        )

    @patch("pathlib.Path.open", new_callable=mock_open)
    @patch("base_collectors.collector.datetime")
    def test_writing_health_check(self, mocked_datetime: Mock, mocked_open: Mock):
        """Test that the current time is written to the health check file."""
        mocked_datetime.now.return_value = now = datetime.now(tz=UTC)
        self.collector.record_health()
        mocked_open.assert_called_once_with("w", encoding="utf-8")
        mocked_open().write.assert_called_once_with(now.isoformat())

    @patch("pathlib.Path.open")
    @patch("logging.error")
    def test_fail_writing_health_check(self, mocked_log: Mock, mocked_open: Mock):
        """Test that a failure to open the health check file is logged, but otherwise ignored."""
        mocked_open.side_effect = OSError("Some error")
        self.collector.record_health()
        mocked_log.assert_called_once_with(
            "Could not write health check time stamp to %s",
            pathlib.Path("/home/collector/health_check.txt"),
            exc_info=True,
        )
