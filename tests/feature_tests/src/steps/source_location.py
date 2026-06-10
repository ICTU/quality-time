"""Step implementations for source locations."""

from typing import TYPE_CHECKING

from asserts import assert_equal, assert_false
from behave import then, when

from item import get_item

if TYPE_CHECKING:
    from behave.runner import Context


@when('the client sets the source location parameter {parameter} to "{value}"')
def change_source_location_parameter(context: Context, parameter: str, value: str) -> None:
    """Change the source location parameter to value."""
    context.post(
        f"source_location/{context.uuid['source_location']}/parameter/{parameter}",
        json={parameter: value},
    )


@when("the client gets the source location")
def get_source_location(context: Context) -> None:
    """Get the source location."""
    context.get(f"source_location/{context.uuid['source_location']}")


@when("the client gets a non-existing source location")
def get_non_existing_source_location(context: Context) -> None:
    """Get a non-existing source location."""
    context.get("source_location/non-existing-source-location")


@then('the source location response has {key} "{value}"')
def check_source_location_response(context: Context, key: str, value: str) -> None:
    """Check that the source location returned by the server has the expected value for the key."""
    assert_equal(value, context.response.json()["source_location"][key])


@when("the client sets the source location of the source")
def set_source_location_of_source(context: Context) -> None:
    """Set the source location of the source to the most recently created source location."""
    context.post(
        f"source/{context.uuid['source']}/attribute/source_location",
        json={"source_location": context.uuid["source_location"]},
    )


@when('the client attempts to add a source_location with type "{source_type}"')
def try_to_create_source_location(context: Context, source_type: str) -> None:
    """Try to create a source location with a source type that has no locations."""
    context.post(f"source_location/new/{context.uuid['report']}", json={"type": source_type})


@then("the source has the source location")
def check_source_has_source_location(context: Context) -> None:
    """Check that the source refers to the most recently created source location."""
    source = get_item(context, "source")
    assert_equal(context.uuid["source_location"], source["source_location"])


@then("the last request failed")
def check_request_failed(context: Context) -> None:
    """Check that the most recent request failed."""
    json = context.response.json()
    assert_false(json["ok"])
