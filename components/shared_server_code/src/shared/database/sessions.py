"""Sessions collection."""

from typing import cast

import bottle
from pymongo.database import Database

from shared.utils.type import SessionData, SessionId, User


def find_user(database: Database) -> User:
    """Return the user sending the request."""
    session_id = cast(SessionId, bottle.request.get_cookie("session_id"))
    session = find_session(database, session_id)
    return User(session.get("user", ""), session.get("email", ""), session.get("common_name", ""))


def find_session(database: Database, session_id: SessionId) -> SessionData:
    """Return the session."""
    return database.sessions.find_one({"session_id": session_id}) or SessionData()
