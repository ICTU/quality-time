"""Sessions collection."""

import logging
from datetime import datetime
from typing import cast

import bottle
from pymongo.database import Database

from server_utilities.type import SessionId

from .reports import latest_reports_overview


def upsert(
    database: Database, username: str, email: str, session_id: SessionId, session_expiration_datetime: datetime
) -> None:
    """Update the existing session for the user or insert a new session."""
    database.sessions.update(
        dict(user=username),
        dict(
            user=username, email=email, session_id=session_id, session_expiration_datetime=session_expiration_datetime
        ),
        upsert=True,
    )


def delete(database: Database, session_id: SessionId) -> None:
    """Remove the session."""
    database.sessions.delete_one(dict(session_id=session_id))


def valid(database: Database, session_id: SessionId) -> bool:
    """Return whether the session exists in the database and has not expired."""
    if session := _find_session(database, session_id):
        return bool(session.get("session_expiration_datetime", datetime.min) > datetime.now())
    return False  # No session with the requested session id found


def authorized(database: Database, session_id: SessionId) -> bool:
    """Return whether the session's user is authorized to edit contents."""
    if session := _find_session(database, session_id):
        if editors := latest_reports_overview(database).get("editors"):
            return session["email"] in editors
        return True  # No editors defined, so any (logged in) user can edit
    return False


def user(database: Database):
    """Return the user sending the request."""
    session_id = cast(SessionId, bottle.request.get_cookie("session_id"))
    return _find_session(database, session_id)


def _find_session(database: Database, session_id: SessionId):
    """Return the session."""
    return database.sessions.find_one(dict(session_id=session_id))
