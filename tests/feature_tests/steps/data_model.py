"""Step implementations for the data model feature."""

import hashlib

from asserts import assert_equal, assert_true
from behave import then, when  # pylint: disable=no-name-in-module


def md5_hash(string: str) -> str:
    """Return a md5 hash of the string."""
    return hashlib.md5(string.encode("utf-8"), usedforsecurity=False).hexdigest()  # skipcq: PYL-E1123,PTC-W1003


@when("the client gets the most recent data model")
def get_data_model(context):
    """Get the most recent data model."""
    headers = {"If-None-Match": f"W/{md5_hash(context.response.json()['timestamp'])}"} if context.response else {}
    context.get("datamodel", headers=headers)


@when("the client gets a data model from too long ago")
def get_old_data_model(context):
    """Get a data model from too long ago."""
    context.get("datamodel?report_date=2000-07-24T10:59:58+00:00")


@then("the server returns the most recent data model")
def check_data_model(context):
    """Check the data model."""
    assert_true("timestamp" in context.response.json())


@then("the server returns a {http_status_code}")
def check_http_status_code(context, http_status_code):
    """Check that the server returns the specified HTTP status code."""
    assert_equal(str(http_status_code), str(context.response.status_code))


@then("the server returns an empty data model")
def check_too_old_data_model(context):
    """Check that the server returns an empty data model."""
    assert_equal({}, context.response.json())
