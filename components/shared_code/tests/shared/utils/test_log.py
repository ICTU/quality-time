"""Unit tests for the logging utilities."""

import logging
import unittest

from shared.utils.log import get_logger


class LogTest(unittest.TestCase):
    """Unit tests for the log utilities."""

    def test_get_logger(self):
        """Test getting the logger."""
        self.assertEqual("quality_time.shared_code.tests.shared.utils.test_log", get_logger("shared_code").name)

    def test_get_logger_indirectly(self):
        """Test getting the logger via an extra function call."""

        def get_logger_indirectly() -> logging.Logger:
            """Return the logger."""
            return get_logger("component", call_stack_depth=1)

        self.assertEqual("quality_time.component.tests.shared.utils.test_log", get_logger_indirectly().name)
