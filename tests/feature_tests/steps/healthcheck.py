"""Test the healthcheck feature."""

from asserts import assert_equal
from behave import given, when, then  # pylint: disable=no-name-in-module


@given("a healthy {server_type} server")
def healthy_server(context, server_type):  # pylint: disable=unused-argument
    """Server should be healthy by default, so no step implementation needed."""


@when("a client checks the {server_type} server health")
def get_health(context, server_type):
    """Get health status."""
    context.get("health", internal=server_type == "internal")


@then("the {server_type} server answers")
def check_health(context, server_type):  # pylint: disable=unused-argument
    """Check the server health."""
    assert_equal({}, context.response.json())
