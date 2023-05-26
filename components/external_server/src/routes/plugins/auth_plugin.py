"""Route authentication and authorization plugin."""

import logging

import bottle

from shared.database.reports import latest_reports_overview
from shared.database import sessions

from model.session import Session


EDIT_REPORT_PERMISSION = "edit_reports"
EDIT_ENTITY_PERMISSION = "edit_entities"


class AuthPlugin:
    """This plugin checks authentication and authorization for post and delete routes."""

    api = 2

    def __init__(self) -> None:
        self.name = "route-auth"

    @classmethod
    def apply(cls, callback, context):
        """Apply the plugin to the route."""
        config = context.config

        if "authentication_required" not in config and "permissions_required" not in config:  # pragma: no cover
            raise AttributeError(  # pragma: no cover
                f"Neither authentication_required nor permission_required set for endpoint {context.rule}"
            )

        if not config.get("authentication_required", True):
            return callback  # Unauthenticated access allowed

        required_permissions = config.get("permissions_required", [])

        def wrapper(*args, **kwargs):
            """Wrap the route."""
            database = kwargs["database"]
            session_id = str(bottle.request.get_cookie("session_id"))
            session = Session(sessions.find_session(database, session_id))
            if not session.is_valid():
                cls.abort(401, "%s-access to %s denied: session %s not authenticated", context, session_id)

            permissions = latest_reports_overview(database).get("permissions", {})
            for permission in required_permissions:
                authorized_users = permissions.get(permission, [])
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
