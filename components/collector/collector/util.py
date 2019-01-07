"""Utility functions."""

import datetime


def timestamp() -> str:
    """Return the ISO-format version of the current UTC date and time without microseconds."""
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
