"""Unit tests for the base metric collector."""

import unittest
from typing import cast
from unittest.mock import AsyncMock, patch

import aiohttp

from shared.model.metric import Metric

from base_collectors import MetricCollector
from model.measurement import MetricMeasurement

from tests.test_fixtures import METRIC_ID


class MetricCollectorTest(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the metric collector."""

    async def test_collect_without_sources_but_with_issues(self):
        """Test that the status of issues is collected even when the metric has no sources."""
        metric = Metric(
            {},
            {
                "sources": {},
                "issue_ids": ["FOO-21"],
                "issue_tracker": {"type": "jira", "parameters": {"url": "https://jira"}},
            },
            METRIC_ID,
        )
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [{}]
        with patch("aiohttp.ClientSession.get", AsyncMock(return_value=mock_async_get_request)):
            async with aiohttp.ClientSession() as session:
                metric_measurement = cast(MetricMeasurement, await MetricCollector(session, metric).collect())
        self.assertEqual("FOO-21", metric_measurement.issue_statuses[0].issue_id)
        self.assertEqual([], metric_measurement.sources)
