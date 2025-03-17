"""Logging utilities."""

import logging
import sys


def get_logger(component_name: str, call_stack_depth: int = 0) -> logging.Logger:
    """Return the logger for the given component and the caller's module."""
    # Get the module name from the caller's stack frame so we can add it to the logger name:
    module_name = sys._getframe(call_stack_depth + 1).f_globals["__name__"]  # noqa: SLF001
    return logging.getLogger(f"quality_time.{component_name}.{module_name}")
