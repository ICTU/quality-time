"""Date and time utilities."""

import re
from datetime import datetime, timedelta
from typing import Final

from dateutil.parser import parse
from dateutil.tz import tzlocal, tzutc

from .functions import decimal_round_half_up

MIN_DATETIME: Final = datetime.min.replace(tzinfo=tzutc())
MAX_DATETIME: Final = datetime.max.replace(tzinfo=tzutc())


def days_ago(date_time: datetime) -> int:
    """Return the days since the date/time."""
    difference = (datetime.now(tz=date_time.tzinfo) - date_time).days
    return max(difference, 0)


def days_to_go(date_time: datetime) -> int:
    """Return the days remaining until the date/time."""
    difference = (date_time - datetime.now(tz=date_time.tzinfo)).days + 1
    return max(difference, 0)


def parse_datetime(text: str) -> datetime:
    """Parse the datetime from the text. If the text does not contain a timezone add the local timezone."""
    date_time = parse(text)
    return date_time.replace(tzinfo=tzlocal()) if date_time.tzinfo is None else date_time


def parse_duration(text: str) -> int:
    """Parse the duration in minutes from the text. Expects '<nr>h <nr>m <nr>s' with each unit being optional."""
    units = ("hours", "minutes", "seconds")
    duration_regexp = r"\s*".join(rf"((?P<{unit}>\d+){unit[0]})?" for unit in units)
    if not (match := re.fullmatch(duration_regexp, text.strip())):
        return 0
    hours, minutes, seconds = [int(match.group(unit) or 0) for unit in units]
    return decimal_round_half_up(60 * hours + minutes + seconds / 60)


def datetime_from_parts(  # noqa: PLR0913
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
) -> datetime:
    """Create a datetime from date and time parts and add the local timezone."""
    return datetime(year, month, day, hour, minute, second, tzinfo=tzlocal())


def datetime_from_timestamp(timestamp: float) -> datetime:
    """Create a datetime from a timestamp in milliseconds and add the local timezone."""
    return datetime.fromtimestamp(timestamp / 1000.0, tz=tzlocal())


def minutes(duration: timedelta) -> int:
    """Return the number of minutes in the duration."""
    return duration.days * 24 * 60 + round(duration.seconds / 60)
