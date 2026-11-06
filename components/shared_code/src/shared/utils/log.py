"""Logging utilities."""

import logging
import sys

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FORMAT = "%(asctime)s %(levelname)-8s %(filename)s:%(lineno)d %(message)s"


def get_logger(component_name: str, call_stack_depth: int = 0) -> logging.Logger:
    """Return the logger for the given component and the caller's module."""
    # Get the module name from the caller's stack frame so we can add it to the logger name:
    module_name = sys._getframe(call_stack_depth + 1).f_globals["__name__"]  # noqa: SLF001
    return logging.getLogger(f"quality_time.{component_name}.{module_name}")


def init_logging(level: str) -> logging.Logger:
    """Initialize the logging and return the root logger.

    Write each log record on a single line, so log aggregators see one record per line.
    """
    handler = logging.StreamHandler(sys.stdout)
    logging.basicConfig(datefmt=DATE_FORMAT, format=LOG_FORMAT, handlers=[handler], force=True)
    logger = logging.getLogger()
    logger.setLevel(level)
    # The MongoDB client logs every command, connection, and server selection at debug level, which drowns out the
    # Quality-time debug messages, so never let it log below info level:
    logging.getLogger("pymongo").setLevel(max(logger.level, logging.INFO))
    return logger
