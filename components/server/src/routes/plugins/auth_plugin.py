"""Route authentication and authorization plugin."""

import logging

import bottle

from database import sessions


class AuthPlugin:  # pylint: disable=too-few-public-methods
    """This plugin checks authentication and authorization for post and delete routes."""

    api = 2

    def __init__(self) -> None:
        self.name = "route-auth"

    @classmethod
    def apply(cls, callback, context):
        """Apply the plugin to the route."""
        path = context.rule.strip("/").split("/")
        if context.method not in ("DELETE", "POST") or path[-1] == "login" or path[0] == "internal-api":
            return callback  # Unauthenticated access allowed

        def wrapper(*args, **kwargs):
            """Wrap the route."""
            session_id = str(bottle.request.get_cookie("session_id"))
            if not sessions.valid(kwargs["database"], session_id):
                cls.abort(401, "%s-access to %s denied: session %s not authenticated", context, session_id)
            if not sessions.authorized(kwargs["database"], session_id):
                cls.abort(403, "%s-access to %s denied: session %s not authorized", context, session_id)
            return callback(*args, **kwargs)

        # Replace the route callback with the wrapped one.
        return wrapper

    @staticmethod
    def abort(status_code: int, message: str, context, session_id: str) -> None:
        """Log the message and abort."""
        logging.warning(message, context.method, context.rule, session_id)
        bottle.abort(status_code, bottle.HTTP_CODES[status_code])
