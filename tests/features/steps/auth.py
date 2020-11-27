"""Steps for authentication."""

from asserts import assert_equal, assert_false
from behave import given, then, when


@given("a logged-in client")
@when("{username} logs in")
def logged_in_client(context, username="admin"):
    """Log in the client."""
    context.post("login", dict(username=username, password="admin" if username == "admin" else "secret"))


@given("a logged-out client")
@when("the client logs out")
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
def check_unauthenticated(context):
    """Check that the server responded with an authenticated error message."""
    assert_equal(401, context.response.status_code)


@then("the server tells the client they are not authorized")
def check_unauthorized(context):
    """Check that the server responded with an unauthorized error message."""
    assert_equal(403, context.response.status_code)
