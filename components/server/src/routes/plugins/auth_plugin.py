"""Route authentication and authorization plugin."""

import logging

import bottle

from database import sessions
from database.reports import latest_reports_overview
from model.session import Session


class AuthPlugin:  # pylint: disable=too-few-public-methods
    """This plugin checks authentication and authorization for post and delete routes."""

    api = 2

    def __init__(self) -> None:
        self.name = "route-auth"

    @classmethod
    def apply(cls, callback, context):
        """Apply the plugin to the route."""
        path = context.rule.strip("/").split("/")

        if path[-1] == "login" or path[0] == "internal-api":
            return callback  # Unauthenticated access allowed

        if context.method == "GET" and not (len(path) == 5 and path[2] == "report" and path[4] == "json"):
            return callback  # Unauthenticated access allowed

        def wrapper(*args, **kwargs):
            """Wrap the route."""
            database = kwargs["database"]
            session_id = str(bottle.request.get_cookie("session_id"))
            session = Session(sessions.find_session(database, session_id))
            if not session.is_valid():
                cls.abort(401, "%s-access to %s denied: session %s not authenticated", context, session_id)
            authorized_users = latest_reports_overview(database).get("editors")
            if not session.is_authorized(authorized_users):
                cls.abort(403, "%s-access to %s denied: session %s not authorized", context, session_id)
            return callback(*args, **kwargs)

        # Replace the route callback with the wrapped one.
        return wrapper

    @staticmethod
    def abort(status_code: int, message: str, context, session_id: str) -> None:
        """Log the message and abort."""
        logging.warning(message, context.method, context.rule, session_id)
        bottle.abort(status_code, bottle.HTTP_CODES[status_code])
