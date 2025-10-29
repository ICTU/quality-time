"""Utility functions."""

import hashlib
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING

from dateutil.tz import tzutc

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from .type import Direction


def iso_timestamp() -> str:
    """Return the ISO-format version of the current UTC date and time without microseconds."""
    return datetime.now(tz=tzutc()).replace(microsecond=0).isoformat()


def percentage(numerator: int, denominator: int, direction: Direction) -> int:
    """Return the rounded percentage: numerator / denominator * 100%."""
    if denominator == 0:  # pragma: no feature-test-cover
        return 0 if direction == "<" else 100
    return int((100 * Decimal(numerator) / Decimal(denominator)).to_integral_value(ROUND_HALF_UP))


def first[T](sequence: Sequence[T], where: Callable[[T], bool] = lambda _item: True) -> T:
    """Return the first item in the sequence."""
    return next(item for item in sequence if where(item))  # pragma: no feature-test-cover


def md5_hash(string: str) -> str:
    """Return a md5 hash of the string."""
    md5 = hashlib.md5(string.encode("utf-8"), usedforsecurity=False)
    return md5.hexdigest()


def slugify(name: str) -> str:
    """Return a slugified version of the name."""
    # Add type to prevent mypy complaining that 'Argument 1 to "maketrans" of "str" has incompatible type...'
    char_mapping: dict[str, str | int | None] = {" ": "-", "(": "", ")": "", "/": ""}
    slug = name.lower().translate(str.maketrans(char_mapping))
    return f"#{slug}"  # The hash isn't really part of the slug, but to prevent duplication it is included anyway
