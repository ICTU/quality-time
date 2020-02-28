"""Utility functions."""

from datetime import datetime, timezone
from typing import Callable, Hashable, Iterable, Iterator, Set, TypeVar
import hashlib
import re
import uuid as _uuid

# Bandit complains that "Using autolink_html to parse untrusted XML data is known to be vulnerable to XML attacks",
# but we give autolink_html clean html, so ignore the warning:
from lxml.html.clean import autolink_html, clean_html  # nosec, pylint: disable=no-name-in-module
import bottle

from server_utilities.type import ReportId


def iso_timestamp() -> str:
    """Return the ISO-format version of the current UTC date and time without microseconds."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def report_date_time() -> str:
    """Return the report date requested as query parameter."""
    report_date_string = dict(bottle.request.query).get("report_date")
    return str(report_date_string).replace("Z", "+00:00") if report_date_string else iso_timestamp()


def uuid() -> ReportId:
    """Return a UUID."""
    return ReportId(str(_uuid.uuid4()))


def md5_hash(string: str) -> str:
    """Return a md5 hash of the string."""
    return hashlib.md5(string.encode("utf-8")).hexdigest()  # nosec, Not used for cryptography


def sanitize_html(html_text: str) -> str:
    """Clean dangerous tags from the HTML and convert urls into anchors."""
    sanitized_html = str(autolink_html(clean_html(html_text)))
    # The clean_html function creates HTML elements. That means if the user enters a simple text string it gets
    # enclosed in a <p> tag. Remove it to not confuse users that haven't entered any HTML:
    if sanitized_html.count("<") == 2:
        sanitized_html = re.sub("</?p>", "", sanitized_html)
    return sanitized_html


Item = TypeVar('Item')


def unique(items: Iterable[Item], get_key: Callable[[Item], Hashable] = lambda item: item) -> Iterator[Item]:
    """Return the unique items in the list."""
    seen: Set[Hashable] = set()
    for item in items:
        if (key := get_key(item)) not in seen:
            seen.add(key)
            yield item
