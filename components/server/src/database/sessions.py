"""Sessions collection."""

from datetime import datetime

from pymongo.database import Database


def upsert(database: Database, username: str, session_id: str, session_expiration_datetime: datetime) -> None:
    """Update the existing session for the user or insert a new session."""
    database.sessions.update(
        dict(user=username),
        dict(user=username, session_id=session_id, session_expiration_datetime=session_expiration_datetime),
        upsert=True)


def delete(database: Database, session_id: str) -> None:
    """Remove the session."""
    database.sessions.delete_one(dict(session_id=session_id))


def valid(database: Database, session_id: str) -> bool:
    """Return whether the session is present in the database and has not expired."""
    session = database.sessions.find_one(dict(session_id=session_id))
    return session.get("session_expiration_datetime", datetime.min) > datetime.now() if session else False
