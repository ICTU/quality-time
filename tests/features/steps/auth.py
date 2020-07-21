"""Steps for authentication."""

from asserts import assert_equal
from behave import given, then


@given("a logged-in client")
def logged_in_client(context):
    """Log in the client."""
    context.post("login", dict(username="admin", password="admin"))


@given("a logged-out client")
def logged_out_client(context):
    """Log out the client."""
    context.post("logout")


@then("the server tells the client to log in")
def check_unauthorized(context):
    """Check that the server responded with an unauthorized error message."""
    assert_equal(401, context.response.status_code)
