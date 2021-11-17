"""Server info."""

import bottle


QUALITY_TIME_VERSION = "3.28.0-rc.3"


@bottle.get("/api/v3/server", authentication_required=False)
def get_server():
    """Return the server info."""
    return dict(version=QUALITY_TIME_VERSION)
