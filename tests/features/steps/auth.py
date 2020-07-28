"""Steps for authentication."""

from asserts import assert_equal, assert_false
from behave import given, then, when


@given("a logged-in client")
def logged_in_client(context):
    """Log in the client."""
    context.post("login", dict(username="admin", password="admin"))


@given("a logged-out client")
def logged_out_client(context):
    """Log out the client."""
    context.post("logout")


@when("the client tries to log in with incorrect credentials")
def log_in_with_incorrect_credentials(context):
    """Try to log in with incorrect credentials."""
    context.post("login", dict(username="admin", password="wrong"))


@then("the server tells the client the credentials are incorrect")
def check_invalid_credentials(context):
    """Check that the server responded that the credentials are invalid."""
    assert_false(context.response.json()["ok"])


@then("the server tells the client to log in")
def check_unauthorized(context):
    """Check that the server responded with an unauthorized error message."""
    assert_equal(401, context.response.status_code)
