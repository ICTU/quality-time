"""Step implementations for server info."""

from typing import TYPE_CHECKING

from asserts import assert_equal, assert_in
from behave import given, then, when

if TYPE_CHECKING:
    from behave.runner import Context


@when("the client gets the server information")
def get_server_info(context: Context) -> None:
    """Get the server info."""
    with context.external_api():
        context.server_info = context.get("server")


@then("the server information is returned")
def server_info(context: Context) -> None:
    """Check the server info."""
    assert_equal(["version"], list(context.server_info.keys()))


@then("the server returns a {http_status_code}")
def check_http_status_code(context: Context, http_status_code: str) -> None:
    """Check that the server returns the specified HTTP status code."""
    assert_equal(str(http_status_code), str(context.response.status_code))


@given("a healthy server")
def healthy_server(_context: Context) -> None:
    """Server should be healthy by default, so no step implementation needed."""


@when("a client checks the server health")
def get_health(context: Context) -> None:
    """Get health status."""
    context.get("health")


@then("the server answers")
def check_health(context: Context) -> None:
    """Check the server health."""
    assert_equal({"healthy": True}, context.response.json())


@when("the client gets the server documentation")
def get_server_docs(context: Context) -> None:
    """Get the server documentation."""
    with context.external_api():
        context.server_docs = context.get("docs")


@then("the server documentation is returned")
def server_docs(context: Context) -> None:
    """Check the server documentation."""
    assert_in("/api/v3/login", list(context.server_docs.keys()))
