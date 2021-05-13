"""Server info."""

import bottle


QUALITY_TIME_VERSION = "3.21.1-rc.3"


@bottle.get("/api/v3/server", authentication_required=False)
def get_server():
    """Return the server info."""
    return dict(version=QUALITY_TIME_VERSION)
