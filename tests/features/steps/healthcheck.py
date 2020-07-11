"""Test the healthcheck feature."""

from asserts import assert_equal
from behave import when, then


@given("a healthy server")
def healthy_server(context):
    """Server should be healthy by default."""
    pass


@when("a client checks the server health")
def get_health(context):
    """Get health status."""
    context.api = "health"


@then("the server answers")
def check_health(context):
    """Check the server health."""
    assert_equal({}, context.get())
