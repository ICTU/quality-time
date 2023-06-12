"""Server info."""

import bottle


QUALITY_TIME_VERSION = "4.10.0"


@bottle.get("/api/v3/server", authentication_required=False)
def get_server():
    """Return the server info."""
    return {"version": QUALITY_TIME_VERSION}
