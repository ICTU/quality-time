"""Server info."""

import bottle


QUALITY_TIME_VERSION = "3.31.0-rc.4"


@bottle.get("/api/v3/server", authentication_required=False)
def get_server():
    """Return the server info."""
    return dict(version=QUALITY_TIME_VERSION)
