"""Logger utilities."""

import logging

from shared.utils.log import get_logger as _get_logger


def get_logger() -> logging.Logger:
    """Return the logger for the current component and the caller's module."""
    return _get_logger("collector", call_stack_depth=1)
