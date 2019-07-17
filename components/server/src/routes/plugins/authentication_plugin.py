"""Route authentication plugin."""

import bottle
import logging

from database import sessions


class AuthenticationPlugin:  # pylint: disable=too-few-public-methods
    """This plugin validates the session id for post routes. If not valid, an error is raised."""

    api = 2

    def __init__(self) -> None:
        self.name = "route-authentication"

    @staticmethod
    def apply(callback, context):
        """Apply the plugin to the route."""

        if context.method != "POST" or context.rule in ("/login", "/measurements"):
            return callback

        def wrapper(*args, **kwargs):
            """Wrap the route."""
            session_id = str(bottle.request.get_cookie("session_id"))
            if sessions.valid(kwargs["database"], session_id):
                return callback(*args, **kwargs)
            logging.warning("Post attemped to %s with invalid session id %s", context.rule, session_id)
            # This doesn't work in Bottle 0.12.16, see https://github.com/bottlepy/bottle/issues/1125:
            # bottle.abort(401, "Access denied")
            return dict(ok=False)

        # Replace the route callback with the wrapped one.
        return wrapper
