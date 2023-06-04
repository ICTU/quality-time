"""Unit tests for the collector main script."""

import logging
import unittest
from unittest.mock import AsyncMock, Mock, patch

from quality_time_collector import collect


class CollectorTestCase(unittest.IsolatedAsyncioTestCase):
    """Unit tests for starting the collector."""

    @patch("base_collectors.Collector.start")
    async def test_start(self, mocked_start):
        """Test that the collector is started."""
        await collect()
        mocked_start.assert_called_once()

    @patch("base_collectors.Collector.start", AsyncMock())
    async def test_default_log_level(self):
        """Test the default logging level."""
        await collect()
        self.assertEqual("WARNING", logging.getLevelName(logging.getLogger().getEffectiveLevel()))

    @patch("base_collectors.Collector.start", AsyncMock())
    @patch("os.getenv", Mock(return_value="DEBUG"))
    async def test_change_log_level(self):
        """Test that the logging level can be changed."""
        await collect()
        self.assertEqual("DEBUG", logging.getLevelName(logging.getLogger().getEffectiveLevel()))
