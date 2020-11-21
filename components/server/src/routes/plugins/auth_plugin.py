"""Route authentication and authorization plugin."""

import logging

import bottle

from database import sessions


class AuthPlugin:  # pylint: disable=too-few-public-methods
    """This plugin checks authentication and authorization for post and delete routes."""

    api = 2

    def __init__(self) -> None:
        self.name = "route-auth"

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
                logging.warning(
                    "%s-access to %s denied: session %s not authenticated", context.method, context.rule, session_id
                )
                bottle.abort(401, "Access denied")
            if not sessions.authorized(kwargs["database"], session_id):
                logging.warning(
                    "%s-access to %s denied: session %s not authorized", context.method, context.rule, session_id
                )
                bottle.abort(403, "Forbidden")
            return callback(*args, **kwargs)

        # Replace the route callback with the wrapped one.
        return wrapper
