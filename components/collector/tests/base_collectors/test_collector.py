"""Unit tests for the collector main script."""

from __future__ import annotations

import asyncio
import logging
import pathlib
import unittest
from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock, _patch, call, mock_open, patch

import aiohttp
import mongomock

import quality_time_collector
from base_collectors import Collector, config

from tests.fixtures import METRIC_ID, METRIC_ID2, SOURCE_ID, SUBJECT_ID, create_report


@patch("model.entity.iso_timestamp", new=Mock(return_value="2023-01-01"))
class CollectorTest(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the collection methods."""

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
        self.database = self.client["quality_time_db"]
        self.collector = Collector(self.database)
        self.database["reports"].insert_one(create_report())

    @staticmethod
    def _patched_get(mock_async_get_request: AsyncMock, side_effect=None) -> _patch[AsyncMock]:
        """Return a patched version of aiohttp.ClientSession.get()."""
        mock = AsyncMock(side_effect=side_effect) if side_effect else AsyncMock(return_value=mock_async_get_request)
        return patch("aiohttp.ClientSession.get", mock)

    async def _fetch_measurements(self, mock_async_get_request, number=1, side_effect=None) -> None:
        """Fetch the measurements with patched get method."""
        with self._patched_get(mock_async_get_request, side_effect):
            async with aiohttp.ClientSession() as session:
                for _ in range(number):
                    self.collector.collect_metrics(session)
                    await asyncio.gather(*self.collector.running_tasks)  # Wait for the running tasks to finish

    def expected_source(self, **kwargs: str | None) -> dict[str, str | None | list[dict[str, str]]]:
        """Create an expected source."""
        connection_error = kwargs.get("connection_error")
        entities = kwargs.get(
            "entities",
            [
                {
                    "name": "a dependency",
                    "key": "a dependency@?",
                    "version": "unknown",
                    "latest": "unknown",
                    "first_seen": "2023-01-01",
                },
            ],
        )
        return {
            "api_url": str(kwargs.get("api_url", self.url)),
            "landing_url": str(kwargs.get("landing_url", self.url)),
            "value": None if connection_error else str(kwargs.get("value", "1")),
            "total": None if connection_error else str(kwargs.get("total", "1")),
            "entities": [] if connection_error else entities,
            "connection_error": connection_error,
            "parse_error": None,
            "source_uuid": SOURCE_ID,
        }

    def expected_measurement(
        self,
        *,
        source_parameter_hash: str = "0f6df164677525409f6269ec97e4118d",
        metric_uuid: str = "metric_uuid",
        **expected_source_kwargs,
    ) -> dict[str, bool | list | str]:
        """Create an expected inserted measurement."""
        return {
            "has_error": "connection_error" in expected_source_kwargs,
            "sources": [self.expected_source(**expected_source_kwargs)],
            "metric_uuid": metric_uuid,
            "report_uuid": "report1",
            "source_parameter_hash": source_parameter_hash,
        }

    async def test_fetch_successful(self):
        """Test fetching a test metric."""
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [self.pip_json]
        with patch(self.create_measurement) as post:
            await self._fetch_measurements(mock_async_get_request)
        post.assert_called_once_with(self.database, self.expected_measurement())

    async def test_fetch_successful_with_landing_url(self):
        """Test fetching a test metric with a landing URL."""
        report = create_report()
        report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]["parameters"]["landing_url"] = (
            "https://example.org"
        )
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [self.pip_json]
        with patch(self.create_measurement) as post:
            self.client["quality_time_db"]["reports"].insert_one(report)
            await self._fetch_measurements(mock_async_get_request)
        post.assert_called_once_with(
            self.database,
            self.expected_measurement(
                source_parameter_hash="86ca213b598583330e2290438f2417a2",
                landing_url="https://example.org",
            ),
        )

    async def test_fetch_without_sources(self):
        """Test fetching measurement for a metric without sources."""
        report_with_no_source = create_report()
        report_with_no_source["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"] = {}
        mock_async_get_request = AsyncMock()
        with patch(self.create_measurement) as post:
            self.client["quality_time_db"]["reports"].insert_one(report_with_no_source)
            await self._fetch_measurements(mock_async_get_request)
        post.assert_not_called()

    async def test_fetch_with_unsupported_collector(self):
        """Test fetching measurement for a metric with an unsupported source."""
        report_with_unsupported_source = create_report()
        report_with_unsupported_source["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID] = {
            "type": "unsupported_source",
        }
        mock_async_get_request = AsyncMock()
        with patch(self.create_measurement) as post:
            self.client["quality_time_db"]["reports"].insert_one(report_with_unsupported_source)
            await self._fetch_measurements(mock_async_get_request)
        post.assert_not_called()

    async def test_fetch_with_get_error(self):
        """Test fetching measurement when getting the metrics fails."""
        with (
            patch(self.create_measurement) as post,
            patch(
                "base_collectors.collector.get_metrics_from_reports",
                return_value={},
                side_effect=RuntimeError,
            ) as _,
            self.assertRaises(RuntimeError),
        ):
            await self._fetch_measurements(AsyncMock())
        post.assert_not_called()

    async def test_fetch_with_client_error(self):
        """Test fetching measurement when getting measurements fails."""
        with patch(self.create_measurement) as post:
            await self._fetch_measurements(None, side_effect=[aiohttp.ClientConnectionError("error")])
        post.assert_called_once_with(self.database, self.expected_measurement(connection_error="error"))

    async def test_fetch_with_empty_client_error(self):
        """Test fetching measurement when getting measurements fails with an 'empty' exception.

        This can happen when an exception returns an empty string when converted to string.
        """
        with patch(self.create_measurement) as post:
            await self._fetch_measurements(None, side_effect=[aiohttp.ClientPayloadError()])
        post.assert_called_once_with(self.database, self.expected_measurement(connection_error="ClientPayloadError"))

    async def test_fetch_with_post_error(self):
        """Test fetching measurement when posting fails."""
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [self.pip_json]
        with patch(self.create_measurement) as post:
            await self._fetch_measurements(mock_async_get_request)
        post.assert_called_once_with(self.database, self.expected_measurement())

    @patch("asyncio.sleep", AsyncMock(side_effect=[RuntimeError]))
    async def test_collect(self):
        """Test the collect method."""
        with (
            patch("quality_time_collector.get_database", return_value=self.database),
            self.assertRaises(RuntimeError),
        ):
            await quality_time_collector.collect()
        # Wait for the created tasks to finish. As we don't have access to Collector.running_tasks, we wait for all
        # runnings tasks, except the one where this test is running:
        await asyncio.gather(*asyncio.all_tasks() - {asyncio.current_task()})
        measurement = next(self.database["measurements"].find({"metric_uuid": "metric_uuid"}))
        # Expect a measurement with a connection error because the runtime error thrown by ascyncio.sleep causes the
        # session to be closed before the measurement can be completed:
        self.assertIn("RuntimeError: Session is closed", measurement["sources"][0]["connection_error"])

    async def test_fetch_twice(self):
        """Test that the metric is skipped on the second fetch."""
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [self.pip_json, self.pip_json]
        with patch(self.create_measurement) as post:
            await self._fetch_measurements(mock_async_get_request, number=2)
        post.assert_called_once_with(self.database, self.expected_measurement())

    @patch.object(config, "MEASUREMENT_LIMIT", 1)
    async def test_fetch_in_batches(self):
        """Test that metrics are fetched in batches."""
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [self.pip_json, self.pip_json]

        with patch(self.create_measurement) as post:
            self.client["quality_time_db"]["reports"].insert_one(create_report(metric_id=METRIC_ID2))
            await self._fetch_measurements(mock_async_get_request, number=2)
        expected_call1 = call(self.database, self.expected_measurement())
        expected_call2 = call(self.database, self.expected_measurement(metric_uuid="metric_uuid2"))
        post.assert_has_calls(calls=[expected_call1, expected_call2])

    @patch.object(config, "MEASUREMENT_LIMIT", 1)
    async def test_prioritize_edited_metrics(self):
        """Test that edited metrics get priority."""
        report1 = create_report()
        report2 = create_report(metric_id=METRIC_ID2)
        edited_url = "https://edited_url"
        report2["subjects"][SUBJECT_ID]["metrics"][METRIC_ID2]["sources"][SOURCE_ID]["parameters"]["url"] = edited_url

        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [self.pip_json, self.pip_json]
        with patch(self.create_measurement) as post:
            self.client["quality_time_db"]["reports"].insert_one(report1)
            self.client["quality_time_db"]["reports"].insert_one(report2)
            await self._fetch_measurements(mock_async_get_request, number=2)

        expected_call1 = call(self.database, self.expected_measurement())
        expected_call2 = call(
            self.database,
            self.expected_measurement(
                source_parameter_hash="ebfcffc74dc017799cb4da33090a9867",
                metric_uuid="metric_uuid2",
                api_url=edited_url,
                landing_url=edited_url,
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
        with patch(self.create_measurement) as post:
            self.client["quality_time_db"]["reports"].insert_one(report_without_url_parameter)
            await self._fetch_measurements(mock_async_get_request)
        post.assert_not_called()

    async def test_missing_mandatory_parameter_with_default_value(self):
        """Test that a metric with sources and a missing mandatory parameter that has a default value is not skipped."""
        self.metrics["metric_uuid"]["sources"]["source_id"] = {"type": "manual_number"}
        report_without_mandatory_parameter = create_report()
        report_without_mandatory_parameter["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID] = {
            "type": "manual_number",
        }
        mock_async_get_request = AsyncMock()
        with patch(self.create_measurement) as post:
            self.client["quality_time_db"]["reports"].insert_one(report_without_mandatory_parameter)
            await self._fetch_measurements(mock_async_get_request)
        post.assert_called_once_with(
            self.database,
            self.expected_measurement(
                source_parameter_hash="8c3b464958e9ad0f20fb2e3b74c80519",
                value="0",
                total="100",
                entities=[],
                api_url="",
                landing_url="",
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
    @patch("logging.getLogger")
    def test_fail_writing_health_check(self, mocked_log: Mock, mocked_open: Mock):
        """Test that a failure to open the health check file is logged, but otherwise ignored."""
        logger = mocked_log.return_value = Mock()
        mocked_open.side_effect = OSError("Some error")
        self.collector.record_health()
        logger.error.assert_called_once_with(
            "Could not write health check time stamp to %s: %s",
            pathlib.Path("/home/collector/health_check.txt"),
            mocked_open.side_effect,
        )
