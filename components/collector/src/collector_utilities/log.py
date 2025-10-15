"""Logger utilities."""

from typing import TYPE_CHECKING

from shared.utils.log import get_logger as _get_logger

if TYPE_CHECKING:
    from logging import Logger


def get_logger() -> Logger:
    """Return the logger for the current component and the caller's module."""
    return _get_logger("collector", call_stack_depth=1)
