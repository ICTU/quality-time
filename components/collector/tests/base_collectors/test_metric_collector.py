"""Unit tests for the base metric collector."""

import unittest
from unittest.mock import AsyncMock, patch

import aiohttp

from base_collectors import MetricCollector


class MetricCollectorTest(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the metric collector."""

    async def test_collect_without_sources_but_with_issues(self):
        """Test that the status of issues is collected even when the metric has no sources."""
        metric = {
            "sources": {},
            "issue_ids": ["FOO-21"],
            "issue_tracker": {"type": "jira", "parameters": {"url": "https://jira"}},
        }
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = [{}]
        with patch("aiohttp.ClientSession.get", AsyncMock(return_value=mock_async_get_request)):
            async with aiohttp.ClientSession() as session:
                metric_measurement = await MetricCollector(session, metric).collect()
        self.assertEqual("FOO-21", metric_measurement.issue_statuses[0].issue_id)
        self.assertEqual([], metric_measurement.sources)
