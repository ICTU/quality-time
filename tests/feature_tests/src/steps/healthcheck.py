"""Test the healthcheck feature."""

from asserts import assert_equal
from behave import given, then, when
from behave.runner import Context


@given("a healthy {_server_type} server")
def healthy_server(_context: Context, _server_type: str) -> None:
    """Server should be healthy by default, so no step implementation needed."""


@when("a client checks the {server_type} server health")
def get_health(context: Context, server_type: str) -> None:
    """Get health status."""
    context.get("health", internal=server_type == "internal")


@then("the {_server_type} server answers")
def check_health(context: Context, _server_type: str) -> None:
    """Check the server health."""
    assert_equal({}, context.response.json())
