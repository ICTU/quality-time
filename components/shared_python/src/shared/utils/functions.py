"""Utility functions."""

from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
import hashlib

from .type import Direction


def iso_timestamp() -> str:
    """Return the ISO-format version of the current UTC date and time without microseconds."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def days_ago(date_time: datetime) -> int:
    """Return the days since the date/time."""
    return max(0, (datetime.now(tz=date_time.tzinfo) - date_time).days)


def percentage(numerator: int, denominator: int, direction: Direction) -> int:
    """Return the rounded percentage: numerator / denominator * 100%."""
    if denominator == 0:
        return 0 if direction == "<" else 100
    return int((100 * Decimal(numerator) / Decimal(denominator)).to_integral_value(ROUND_HALF_UP))


def md5_hash(string: str) -> str:
    """Return a md5 hash of the string."""
    return hashlib.md5(string.encode("utf-8")).hexdigest()  # noqa: DUO130, # nosec # Not used for cryptography


def report_date_time(report_date_string) -> str:
    """Return the report date requested as query parameter if it's in the past, else return an empty string."""
    if report_date_string:
        iso_report_date_string = str(report_date_string).replace("Z", "+00:00")
        if iso_report_date_string < iso_timestamp():
            return iso_report_date_string
    return ""
