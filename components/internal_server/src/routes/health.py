"""Server health endpoint."""

import bottle


@bottle.get("/api/health")
def get_health():
    """Return the server health."""
    return {}
