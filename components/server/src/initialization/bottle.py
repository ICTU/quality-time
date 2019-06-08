"""Initialize bottle."""

import bottle

from ..route_authentication_plugin import AuthenticationPlugin


def init_bottle() -> None:
    """Initialize bottle."""
    bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024  # Max size of POST body in bytes
    bottle.install(AuthenticationPlugin())
