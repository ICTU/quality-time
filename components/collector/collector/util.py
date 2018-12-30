"""Utility functions."""

import datetime


def timestamp():
    """Return the ISO-format version of the current UTC date and time without microseconds."""
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat()
