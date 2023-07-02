"""Shared datetime utilities."""

from datetime import datetime

from dateutil.tz import tzlocal


def now() -> datetime:
    """Return now in the local timezone."""
    return datetime.now(tz=tzlocal())
