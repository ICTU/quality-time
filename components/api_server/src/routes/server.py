"""Server info."""

import bottle


QUALITY_TIME_VERSION = "5.17.1-rc.0"


@bottle.get("/api/v3/server", authentication_required=False)
def get_server():
    """Return the server info."""
    return {"version": QUALITY_TIME_VERSION}
