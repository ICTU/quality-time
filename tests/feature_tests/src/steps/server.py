"""Step implementations for server info."""

from asserts import assert_equal
from behave import then, when
from behave.runner import Context


@when("the client gets the server information")
def get_server_info(context: Context) -> None:
    """Get the server info."""
    context.server_info = context.get("server")


@then("the server information is returned")
def server_info(context: Context) -> None:
    """Check the server info."""
    assert_equal(["version"], list(context.server_info.keys()))


@then("the server returns a {http_status_code}")
def check_http_status_code(context: Context, http_status_code: str) -> None:
    """Check that the server returns the specified HTTP status code."""
    assert_equal(str(http_status_code), str(context.response.status_code))
