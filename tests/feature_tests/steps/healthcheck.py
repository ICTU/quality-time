"""Test the healthcheck feature."""

from asserts import assert_equal
from behave import given, when, then


@given("a healthy {server}")
def healthy_server(context, server):
    """Server should be healthy by default, so no step implementation needed."""


@when("a client checks the {server} health")
def get_health(context, server):
    """Get health status."""
    context.get("health", internal_server=server == "internal-server")


@then("the {server} answers")
def check_health(context, server):
    """Check the server health."""
    expected_answer = dict(healthy=True) if server == "internal-server" else {}
    assert_equal(expected_answer, context.response.json())
