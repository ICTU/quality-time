"""Utility functions."""

import datetime
from urllib.parse import urlsplit


def timestamp():
    """Return the ISO-format version of the current UTC date and time without microseconds."""
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat()


def hash_request_url(url):
    """Hash the request url so that it is short enough to be usable as database column id."""
    parts = urlsplit(url)
    return str(hash(parts.path + parts.query))
