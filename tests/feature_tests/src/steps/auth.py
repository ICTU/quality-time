"""Steps for authentication."""

from asserts import assert_equal, assert_false, assert_in
from behave import given, then, when
from behave.runner import Context


@given("a logged-in client")
@when("{username} logs in")
def logged_in_client(context: Context, username: str = "jadoe") -> None:
    """Log in the client."""
    password = "secret"  # nosec, # noqa: S105
    context.post("login", {"username": username, "password": password})


@given("a logged-out client")
@when("the client logs out")
def logged_out_client(context: Context) -> None:
    """Log out the client."""
    context.post("logout")


@when("the client tries to log in with incorrect credentials")
def log_in_with_incorrect_credentials(context: Context) -> None:
    """Try to log in with incorrect credentials."""
    context.post("login", {"username": "jadoe", "password": "wrong"})  # nosec


@when("the client tries to access a non-existing endpoint")
def access_non_existing_endpoint(context: Context) -> None:
    """Try to access non-existing endpoint."""
    context.get("does-not-exist")


@then("the server tells the client the credentials are incorrect")
def check_invalid_credentials(context: Context) -> None:
    """Check that the server responded that the credentials are invalid."""
    assert_false(context.response.json()["ok"])


@then("the server tells the client to log in")
def check_unauthenticated(context: Context) -> None:
    """Check that the server responded with an authenticated error message."""
    assert_equal(401, context.response.status_code)


@then("the server tells the client they are not authorized")
def check_unauthorized(context: Context) -> None:
    """Check that the server responded with an unauthorized error message."""
    assert_equal(403, context.response.status_code)


@then("the server tells the client the endpoint does not exist")
def check_endpoint_does_not_exist(context: Context) -> None:
    """Check that the server responded with a resource does not exist error message."""
    assert_equal(404, context.response.status_code)


@when("the client requests the public key")
def get_public_key(context: Context) -> None:
    """Get the public key."""
    with context.external_api():
        context.public_key = context.get("public_key")


@then("the client receives the public key")
def check_public_key(context: Context) -> None:
    """Check that this is actually a public key."""
    assert_in("public_key", context.public_key)
