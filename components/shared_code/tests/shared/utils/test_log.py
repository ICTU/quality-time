"""Unit tests for the logging utilities."""

import logging
import sys
import unittest
from typing import TYPE_CHECKING, cast

from shared.utils.log import LOG_FORMAT, get_logger, init_logging

if TYPE_CHECKING:
    from logging import Logger


class LogTest(unittest.TestCase):
    """Unit tests for the log utilities."""

    def test_get_logger(self):
        """Test getting the logger."""
        self.assertEqual("quality_time.shared_code.tests.shared.utils.test_log", get_logger("shared_code").name)

    def test_get_logger_indirectly(self):
        """Test getting the logger via an extra function call."""

        def get_logger_indirectly() -> Logger:
            """Return the logger."""
            return get_logger("component", call_stack_depth=1)

        self.assertEqual("quality_time.component.tests.shared.utils.test_log", get_logger_indirectly().name)


class InitLoggingTest(unittest.TestCase):
    """Unit tests for the log initialization."""

    def setUp(self):
        """Save the root logger's handlers and level."""
        self.root_logger = logging.getLogger()
        self.original_handlers = self.root_logger.handlers[:]
        self.original_level = self.root_logger.level

    def tearDown(self):
        """Restore the root logger's handlers and level, and the MongoDB client logger's level."""
        logging.getLogger("pymongo").setLevel(logging.NOTSET)
        for handler in self.root_logger.handlers[:]:
            self.root_logger.removeHandler(handler)
            handler.close()
        self.root_logger.handlers[:] = self.original_handlers
        self.root_logger.setLevel(self.original_level)

    def test_handler(self):
        """Test that the root logger has one stream handler, writing to stdout with the log format."""
        handlers = init_logging("INFO").handlers
        self.assertEqual(1, len(handlers))
        handler = cast(logging.StreamHandler, handlers[0])
        self.assertIsInstance(handler, logging.StreamHandler)
        self.assertIs(sys.stdout, handler.stream)
        self.assertEqual(LOG_FORMAT, cast(logging.Formatter, handler.formatter)._fmt)  # noqa: SLF001

    def test_long_messages_are_not_wrapped(self):
        """Test that the handler formats long messages on a single line."""
        handler = init_logging("INFO").handlers[0]
        message = "Long message " + "x" * 200
        record = logging.LogRecord("name", logging.WARNING, "source_collector.py", 106, message, None, None)
        formatted_record = handler.format(record)
        self.assertNotIn("\n", formatted_record)
        self.assertIn(message, formatted_record)
        self.assertIn("WARNING  source_collector.py:106 Long message", formatted_record)

    def test_init_logging_twice(self):
        """Test that initializing the logging twice leaves one handler."""
        init_logging("INFO")
        self.assertEqual(1, len(init_logging("INFO").handlers))

    def test_level(self):
        """Test that the level is applied to the root logger."""
        self.assertEqual(logging.DEBUG, init_logging("DEBUG").level)

    def test_mongodb_client_does_not_log_debug_messages(self):
        """Test that the MongoDB client logger does not log debug messages, even if the level is debug."""
        init_logging("DEBUG")
        self.assertEqual(logging.INFO, logging.getLogger("pymongo").level)

    def test_mongodb_client_level_follows_level_above_debug(self):
        """Test that the MongoDB client logger has the same level as the root logger if that is above debug."""
        init_logging("WARNING")
        self.assertEqual(logging.WARNING, logging.getLogger("pymongo").level)
