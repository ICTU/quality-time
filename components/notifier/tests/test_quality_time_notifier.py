"""Unit tests for the notifier main script."""

import logging
import os
import unittest
from unittest.mock import AsyncMock, patch

from quality_time_notifier import start_notifications


@patch("quality_time_notifier.notify", AsyncMock())
class NotifierTestCase(unittest.TestCase):
    """Unit tests for the notifier."""

    def test_default_log_level(self):
        """Test the default logging level."""
        start_notifications()
        self.assertEqual("WARNING", logging.getLevelName(logging.getLogger().getEffectiveLevel()))

    @patch.dict(os.environ, {"NOTIFIER_LOG_LEVEL": "DEBUG"})
    def test_change_log_level(self):
        """Test that the logging level can be changed."""
        start_notifications()
        self.assertEqual("DEBUG", logging.getLevelName(logging.getLogger().getEffectiveLevel()))
