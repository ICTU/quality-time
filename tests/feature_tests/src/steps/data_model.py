"""Step implementations for the data model feature."""

import hashlib

from asserts import assert_equal, assert_true
from behave import then, when
from behave.runner import Context


def md5_hash(string: str) -> str:
    """Return a md5 hash of the string."""
    return hashlib.md5(string.encode("utf-8"), usedforsecurity=False).hexdigest()


@when("the client gets the most recent data model")
def get_data_model(context: Context) -> None:
    """Get the most recent data model."""
    headers = {"If-None-Match": f"{md5_hash(context.response.json()['timestamp'])}"} if context.response else {}
    context.get("datamodel", headers=headers)


@when("the client gets a data model from too long ago")
def get_old_data_model(context: Context) -> None:
    """Get a data model from too long ago."""
    context.report_date = "2000-07-24T10:59:58+00:00"
    context.get("datamodel")


@then("the server returns the most recent data model")
def check_data_model(context: Context) -> None:
    """Check the data model."""
    assert_true("timestamp" in context.response.json())


@then("the server returns a {http_status_code}")
def check_http_status_code(context: Context, http_status_code: str) -> None:
    """Check that the server returns the specified HTTP status code."""
    assert_equal(str(http_status_code), str(context.response.status_code))


@then("the server returns an empty data model")
def check_too_old_data_model(context: Context) -> None:
    """Check that the server returns an empty data model."""
    assert_equal({}, context.response.json())
