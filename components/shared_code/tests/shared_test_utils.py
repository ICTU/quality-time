"""Utilities for unit tests, shared across components."""

import functools
import logging
from collections.abc import Callable
from typing import TypeVar

ReturnType = TypeVar("ReturnType")


def disable_logging(func: Callable[..., ReturnType]):
    """Temporarily disable logging."""

    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs) -> ReturnType:
        """Disable logging before calling func and reenable it afterwards."""
        logging.disable(logging.CRITICAL)
        result = func(*args, **kwargs)
        logging.disable(logging.NOTSET)
        return result

    return wrapper_decorator
