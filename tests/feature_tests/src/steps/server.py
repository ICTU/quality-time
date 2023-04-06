"""Step implementations for server info."""

from asserts import assert_equal
from behave import then, when  # pylint: disable=no-name-in-module


@when("the client gets the server information")
def get_server_info(context):
    """Get the server info."""
    context.server_info = context.get("server")


@then("the server information is returned")
def server_info(context):
    """Check the server info."""
    assert_equal(["version"], list(context.server_info.keys()))
