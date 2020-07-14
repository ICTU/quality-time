"""Steps for authentication."""

from behave import given


@given("a logged-in client")
def logged_in_client(context):
    """Log in the client."""
    context.post("login", dict(username="admin", password="admin"))
