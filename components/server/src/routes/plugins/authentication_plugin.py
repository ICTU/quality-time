"""Route authentication plugin."""

import logging

import bottle

from database import sessions


class AuthenticationPlugin:  # pylint: disable=too-few-public-methods
    """This plugin validates the session id for post routes. If not valid, an error is raised."""

    api = 2

    def __init__(self) -> None:
        self.name = "route-authentication"

    @staticmethod
    def apply(callback, context):
        """Apply the plugin to the route."""
        path = context.rule.strip("/").split("/")
        if context.method not in ("DELETE", "POST") or path[-1] == "login" or path[0] == "internal-api":
            return callback  # Unauthenticated access allowed

        def wrapper(*args, **kwargs):
            """Wrap the route."""
            session_id = str(bottle.request.get_cookie("session_id"))
            if not sessions.valid(kwargs["database"], session_id):
                logging.warning("Post attempted to %s with invalid session id %s", context.rule, session_id)
                bottle.abort(401, "Access denied")
            if not sessions.authorized(kwargs["database"], session_id):
                logging.warning("Post attempted to %s with unauthorized session id %s", context.rule, session_id)
                bottle.abort(403, "Forbidden")
            return callback(*args, **kwargs)

        # Replace the route callback with the wrapped one.
        return wrapper
