"""Unit tests for the collector main script."""

import asyncio
import logging
import unittest
from datetime import datetime
from unittest.mock import AsyncMock, Mock, call, mock_open, patch

import aiohttp
import mongomock
from aioresponses import aioresponses

import quality_time_collector
from base_collectors import Collector, get
from tests.fixtures import METRIC_ID, METRIC_ID2, SOURCE_ID, SUBJECT_ID, create_report


class CollectorTest(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the collection methods."""

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
        self.metrics = dict(
            metric_uuid=dict(
                report_uuid="report_uuid",
                addition="sum",
                type="dependencies",
                sources=dict(source_uuid=dict(type="pip", parameters=dict(url=self.url))),
            )
        )
        self.pip_json = [dict(name="a dependency")]
        self.client = mongomock.MongoClient()
        self.client["quality_time_db"]["reports"].insert_one(create_report())

    @staticmethod
    def _patched_get(mock_async_get_request, side_effect=None):
        """Return a patched version of aiohttp.ClientSession.get()."""
        mock = AsyncMock(side_effect=side_effect) if side_effect else AsyncMock(return_value=mock_async_get_request)
        if not side_effect:
            mock_async_get_request.close = Mock()
        return patch("aiohttp.ClientSession.get", mock)

    async def _fetch_measurements(self, mock_async_get_request, number=1, side_effect=None):
        """Fetch the measurements with patched get method."""
        with self._patched_get(mock_async_get_request, side_effect):
            async with aiohttp.ClientSession() as session:
                for _ in range(number):
                    await self.collector.collect_metrics(session)

    def _source(self, **kwargs):
        """Create a source."""
        connection_error = kwargs.get("connection_error")
        entities = kwargs.get(
            "entities", [dict(name="a dependency", key="a dependency@?", version="unknown", latest="unknown")]
        )
        return dict(
            api_url=kwargs.get("api_url", self.url),
            landing_url=kwargs.get("landing_url", self.url),
            value=None if connection_error else kwargs.get("value", "1"),
            total=None if connection_error else kwargs.get("total", "100"),
            entities=[] if connection_error else entities,
            connection_error=connection_error,
            parse_error=None,
            source_uuid="source_uuid",
        )

    @aioresponses()
    async def test_get(self, mocked):
        """Tests get method"""
        mocked.get("http://sonarcloud.com/api/fake_things", status=200, body='{"status": "ok"}')
        session = aiohttp.ClientSession()
        resp = await get(session, "http://sonarcloud.com/api/fake_things")

        assert resp == {"status": "ok"}
        mocked.assert_called_once_with("http://sonarcloud.com/api/fake_things")

    def test_get_with_error(self):
        """Tests get method with error"""
        loop = asyncio.get_event_loop()
        session = AsyncMock()
        session.get.side_effect = [RuntimeError]
        with patch("base_collectors.collector.logging.error") as logger:
            _ = loop.run_until_complete(get(session, "http://sonarcloud.com/api/fake_things"))
        logger.assert_called()

    async def test_fetch_successful(self):
        """Test fetching a test metric."""
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [self.pip_json]
        with patch("base_collectors.collector.create_measurement") as post, patch(
            "shared.initialization.database.client", return_value=self.client
        ):
            await self._fetch_measurements(mock_async_get_request)
        post.assert_called_once_with(
            dict(has_error=False, sources=[self._source()], metric_uuid="metric_uuid", report_uuid="report1"),
        )

    async def test_fetch_without_sources(self):
        """Test fetching measurement for a metric without sources."""
        report_with_no_source = create_report()
        report_with_no_source["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"] = dict()
        mock_async_get_request = AsyncMock()
        with patch("base_collectors.collector.create_measurement") as post, patch(
            "shared.initialization.database.client", return_value=self.client
        ):
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
        with patch("base_collectors.collector.create_measurement") as post, patch(
            "shared.initialization.database.client", return_value=self.client
        ):
            self.client["quality_time_db"]["reports"].insert_one(report_with_unsupported_source)
            await self._fetch_measurements(mock_async_get_request)
        post.assert_not_called()

    async def test_fetch_with_get_error(self):
        """Test fetching measurement when getting the metrics fails."""
        with patch("base_collectors.collector.create_measurement") as post, patch(
            "shared.initialization.database.client", return_value=self.client, side_effect=RuntimeError
        ) as _, self.assertRaises(RuntimeError):
            await self._fetch_measurements(AsyncMock())

        post.assert_not_called()

    async def test_fetch_with_client_error(self):
        """Test fetching measurement when getting measurements fails."""
        mock_async_get_request = AsyncMock()
        mock_async_get_request.close = Mock()
        # mock_async_get_request.json.return_value = self.pip_json
        with patch("base_collectors.collector.create_measurement") as post, patch(
            "shared.initialization.database.client", return_value=self.client
        ):
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
        mock_async_get_request = AsyncMock()
        mock_async_get_request.close = Mock()
        with patch("base_collectors.collector.create_measurement") as post, patch(
            "shared.initialization.database.client", return_value=self.client
        ):
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
        with patch("base_collectors.collector.create_measurement") as post, patch(
            "shared.initialization.database.client", return_value=self.client
        ):
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
        with patch("shared.initialization.database.client", return_value=self.client), self._patched_get(
            mock_async_get_request
        ), patch("base_collectors.collector.create_measurement") as post, self.assertRaises(RuntimeError):
            await quality_time_collector.collect()
        post.assert_called_once_with(
            dict(has_error=False, sources=[self._source()], metric_uuid="metric_uuid", report_uuid="report1"),
        )

    async def test_fetch_twice(self):
        """Test that the metric is skipped on the second fetch."""
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [self.pip_json, self.pip_json]
        with patch("base_collectors.collector.create_measurement") as post, patch(
            "shared.initialization.database.client", return_value=self.client
        ):
            await self._fetch_measurements(mock_async_get_request, number=2)
        post.assert_called_once_with(
            dict(has_error=False, sources=[self._source()], metric_uuid="metric_uuid", report_uuid="report1"),
        )

    @patch.object(Collector, "MEASUREMENT_LIMIT", 1)
    async def test_fetch_in_batches(self):
        """Test that metrics are fetched in batches."""
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [self.pip_json, self.pip_json]

        with patch("base_collectors.collector.create_measurement") as post, patch(
            "shared.initialization.database.client", return_value=self.client
        ):
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
        with patch("base_collectors.collector.create_measurement") as post, patch(
            "shared.initialization.database.client", return_value=self.client
        ):
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
        mock_async_get_request = AsyncMock()
        report_without_url_parameter = create_report()
        report_without_url_parameter["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]["parameters"][
            "url"
        ] = ""
        mock_async_get_request = AsyncMock()
        with patch("base_collectors.collector.create_measurement") as post, patch(
            "shared.initialization.database.client", return_value=self.client
        ):
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
        with patch("base_collectors.collector.create_measurement") as post, patch(
            "shared.initialization.database.client", return_value=self.client
        ):
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
