"""Sessions collection."""

from typing import cast

import bottle
from pymongo.database import Database

from shared.utils.type import SessionId, User


def find_user(database: Database) -> User:
    """Return the user sending the request."""
    session_id = cast(SessionId, bottle.request.get_cookie("session_id"))
    session = find_session(database, session_id) or {}
    return User(session.get("user", ""), session.get("email", ""), session.get("common_name", ""))


def find_session(database: Database, session_id: SessionId):
    """Return the session."""
    return database.sessions.find_one(dict(session_id=session_id))
