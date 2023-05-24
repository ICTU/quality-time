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
