"""Documentation routes."""

import os

import bottle


@bottle.get("/api/v3/docs", authentication_required=False)
def get_api_docs() -> dict[str, dict[str, str]]:
    """Return the API docs."""
    port = os.environ.get("API_SERVER_PORT", "5001")
    return {
        route.rule: {
            "url": f"https://www.quality-time.example.org:{port}{route.rule}",
            "method": route.method,
            "description": route.callback.__doc__,
        }
        for route in bottle.default_app().routes
    }
