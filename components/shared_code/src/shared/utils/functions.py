"""Utility functions."""

from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal

from .type import Direction


def iso_timestamp() -> str:
    """Return the ISO-format version of the current UTC date and time without microseconds."""
    return datetime.now(tz=UTC).replace(microsecond=0).isoformat()


def percentage(numerator: int, denominator: int, direction: Direction) -> int:
    """Return the rounded percentage: numerator / denominator * 100%."""
    if denominator == 0:  # pragma: no feature-test-cover
        return 0 if direction == "<" else 100
    return int((100 * Decimal(numerator) / Decimal(denominator)).to_integral_value(ROUND_HALF_UP))


def first[T](sequence: Sequence[T], where: Callable[[T], bool] = lambda _item: True) -> T:  # type: ignore[name-defined]  # mypy does not yet support PEP 695, Type Parameter Syntax. See https://github.com/python/mypy/issues/15238
    """Return the first item in the sequence."""
    return next(item for item in sequence if where(item))  # pragma: no feature-test-cover
