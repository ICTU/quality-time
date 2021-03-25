"""Documentation routes."""

import os

import bottle


@bottle.get("/api", authentication_required=False)
@bottle.get("/api/<fragment>", authentication_required=False)
@bottle.get("/api/<version>/<fragment>", authentication_required=False)
def get_api(version="", fragment=""):
    """Return the API. Use version and/or fragment to limit the routes returned."""
    port = os.environ.get("SERVER_PORT", "5001")
    routes = [route for route in bottle.default_app().routes if version in route.rule and fragment in route.rule]
    return {
        route.rule: dict(
            url=f"http://www.quality-time.example.org:{port}{route.rule}",
            method=route.method,
            description=route.callback.__doc__,
        )
        for route in routes
    }
