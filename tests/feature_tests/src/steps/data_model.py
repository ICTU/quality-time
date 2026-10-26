"""Step implementations for the data model feature."""

from typing import TYPE_CHECKING

from asserts import assert_equal, assert_true
from behave import then, when

if TYPE_CHECKING:
    from behave.runner import Context


@when("the client gets the most recent data model")
def get_data_model(context: Context) -> None:
    """Get the most recent data model."""
    headers = {"If-None-Match": context.response.headers["ETag"]} if context.response else {}
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


@then("the server returns an empty data model")
def check_too_old_data_model(context: Context) -> None:
    """Check that the server returns an empty data model."""
    assert_equal({}, context.response.json())
