"""Server info."""

import bottle


QUALITY_TIME_VERSION = "3.20.0-rc.1"


@bottle.get("/api/v3/server")
def get_server():
    """Return the server info."""
    return dict(version=QUALITY_TIME_VERSION)
