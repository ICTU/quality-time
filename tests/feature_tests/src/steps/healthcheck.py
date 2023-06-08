"""Test the healthcheck feature."""

from asserts import assert_equal
from behave import given, then, when
from behave.runner import Context


@given("a healthy external server")
def healthy_server(_context: Context) -> None:
    """Server should be healthy by default, so no step implementation needed."""


@when("a client checks the external server health")
def get_health(context: Context) -> None:
    """Get health status."""
    context.get("health")


@then("the external server answers")
def check_health(context: Context) -> None:
    """Check the server health."""
    assert_equal({}, context.response.json())
