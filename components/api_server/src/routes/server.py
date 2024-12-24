"""Server info."""

import bottle

from shared.utils.version import QUALITY_TIME_VERSION


@bottle.get("/api/v3/server", authentication_required=False)
def get_server():
    """Return the server info."""
    return {"version": QUALITY_TIME_VERSION}
