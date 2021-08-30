"""Step implementations for server info."""

from asserts import assert_equal
from behave import then, when


@when("the client gets the {server} information")
def get_server_info(context, server):
    """Get the server info."""
    url = "" if server == "internal-server" else "server"
    context.server_info = context.get(url, internal_server=server == "internal-server")


@then("the {server} information is returned")
def server_info(context, server):
    """Check the server info."""
    if server == "internal-server":
        assert_equal("http://localhost:8000/docs", context.server_info.url)
    else:
        assert_equal(["version"], list(context.server_info.keys()))
