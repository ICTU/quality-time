"""Unit tests for the logging utilities."""

import unittest

from utils.log import get_logger


class LogTest(unittest.TestCase):
    """Unit tests for the log utilities."""

    def test_get_logger(self):
        """Test getting the logger."""
        self.assertEqual("quality_time.api_server.tests.utils.test_log", get_logger().name)
