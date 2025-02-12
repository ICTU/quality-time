"""Health end-point."""

import bottle


@bottle.get("/api/internal/health", authentication_required=False)
def get_health():
    """Return the API-server health."""
    return {"healthy": True}  # For now, server being up means it is healthy
