"""Step implementations for sources."""

from pathlib import Path
from typing import TYPE_CHECKING

from asserts import assert_equal, assert_in
from behave import then, when

from item import get_item

if TYPE_CHECKING:
    from behave.runner import Context


def sanitize_value(value: str) -> str | list[str]:
    """Convert the value if necessary."""
    if value == "None":
        return ""
    if "[" in value:
        # Split the list items and strip the quotes:
        return [item[1:-1] for item in value[1:-1].split(", ")]
    return value


@when('the client sets the source parameter {parameter} to "{value}"')
def change_source_parameter(context: Context, parameter: str, value: str) -> None:
    """Change the source parameter to value."""
    context.post(
        f"source/{context.uuid['source']}/parameter/{parameter}",
        json={parameter: sanitize_value(value)},
    )


@then('the source parameter {parameter} equals "{value}"')
def check_source_parameter(context: Context, parameter: str, value: str) -> None:
    """Check that the source parameter equals value."""
    source = get_item(context, "source")
    assert_equal(sanitize_value(value), source["parameters"][parameter])


@then('the availability status code equals "{status_code}"')
def check_source_parameter_availability_status_code(context: Context, status_code: str) -> None:
    """Check the availability status code."""
    post_response = context.post_response.json()
    if status_code == "None":
        assert_equal({}, post_response.get("availability", {}))
    else:
        assert_equal(status_code, str(post_response["availability"]["status_code"]))


@then('the availability status reason equals "{message1}"')
@then('the availability status reason equals either "{message1}" or "{message2}"')
@then('the availability status reason equals either "{message1}" or "{message2}" or "{message3}"')
def check_source_parameter_availability_reason(
    context: Context,
    message1: str,
    message2: str = "",
    message3: str = "",
) -> None:
    """Check the availability message."""
    post_response = context.post_response.json()
    reason = str(post_response["availability"]["reason"])
    messages = [message for message in (message1, message2, message3) if message]
    assert_in(reason, messages)


@then('"{path}" is returned as source logo')
def check_source_logo(context: Context, path: str) -> None:
    """Check that the correct source logo is returned."""
    source_type = get_item(context, "source")["type"]
    logo_via_server = context.get(f"logo/{source_type}").content
    with Path(path).open("rb") as logo_on_disk:
        assert_equal(logo_via_server, logo_on_disk.read())
