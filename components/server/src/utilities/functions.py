"""Utility functions."""

import uuid as _uuid

import bottle
from shared.utilities.functions import iso_timestamp


def report_date_time() -> str:
    """Return the report date requested as query parameter."""
    report_date_string = dict(bottle.request.query).get("report_date")
    return report_date_string.replace("Z", "+00:00") if report_date_string else iso_timestamp()


def uuid() -> str:
    """Return a UUID."""
    return str(_uuid.uuid4())
