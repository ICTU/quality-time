"""Shared datetime utilities."""

from datetime import datetime

from dateutil.parser import parse
from dateutil.tz import tzlocal


def now() -> datetime:
    """Return now in the local timezone."""
    return datetime.now(tz=tzlocal())


def parse_datetime(text: str) -> datetime:
    """Parse the datetime from the text. If the text does not contain a timezone add the local timezone."""
    date_time = parse(text)
    return date_time.replace(tzinfo=tzlocal()) if date_time.tzinfo is None else date_time
