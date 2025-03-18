"""Route authentication and authorization plugin."""

from collections.abc import Callable

import bottle

from database import sessions
from database.reports import latest_reports_overview
from model.session import Session
from utils.log import get_logger
from utils.type import SessionId


EDIT_REPORT_PERMISSION = "edit_reports"
EDIT_ENTITY_PERMISSION = "edit_entities"


class AuthPlugin:
    """Plugin to check authentication and authorization for post and delete routes."""

    api = 2

    def __init__(self) -> None:
        self.name = "route-auth"

    @classmethod
    def apply[ReturnType](cls, callback: Callable[..., ReturnType], context) -> Callable[..., ReturnType]:
        """Apply the plugin to the route."""
        config = context.config

        if "authentication_required" not in config and "permissions_required" not in config:  # pragma: no cover
            msg = f"Neither authentication_required nor permission_required set for endpoint {context.rule}"
            raise AttributeError(  # pragma: no cover
                msg,
            )

        if not config.get("authentication_required", True):
            return callback  # Unauthenticated access allowed

        required_permissions = config.get("permissions_required", [])

        def wrapper(*args, **kwargs) -> ReturnType:
            """Wrap the route."""
            database = kwargs["database"]
            session_id = SessionId(bottle.request.get_cookie("session_id"))
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
        logger = get_logger()
        logger.warning(message, context.method, context.rule, session_id)
        bottle.abort(status_code, bottle.HTTP_CODES[status_code])
