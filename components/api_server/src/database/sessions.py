"""Sessions collection."""

from typing import cast, TYPE_CHECKING

import bottle

from utils.type import SessionData, SessionId, User

if TYPE_CHECKING:
    from datetime import datetime

    from pymongo.database import Database


def upsert(database: Database, user: User, session_id: SessionId, session_expiration_datetime: datetime) -> None:
    """Update the existing session for the user or insert a new session."""
    database.sessions.replace_one(
        {"user": user.username},
        {
            "user": user.username,
            "email": user.email,
            "common_name": user.common_name,
            "session_id": session_id,
            "session_expiration_datetime": session_expiration_datetime,
        },
        upsert=True,
    )


def delete(database: Database, session_id: SessionId) -> None:
    """Remove the session."""
    database.sessions.delete_one({"session_id": session_id})


def get(database, session_id: SessionId):
    """Return the session object belonging to a session id."""
    return database.sessions.find_one({"session_id": session_id})


def find_user(database: Database) -> User:
    """Return the user sending the request."""
    session_id = cast(SessionId, bottle.request.get_cookie("session_id"))
    session = find_session(database, session_id)
    return User(session.get("user", ""), session.get("email", ""), session.get("common_name", ""))


def find_session(database: Database, session_id: SessionId) -> SessionData:
    """Return the session."""
    return database.sessions.find_one({"session_id": session_id}) or SessionData()
