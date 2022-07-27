"""Sessions collection."""

from datetime import datetime

from pymongo.database import Database

from shared.utils.type import SessionId, User


def upsert(database: Database, user: User, session_id: SessionId, session_expiration_datetime: datetime) -> None:
    """Update the existing session for the user or insert a new session."""
    database.sessions.replace_one(
        dict(user=user.username),
        dict(
            user=user.username,
            email=user.email,
            common_name=user.common_name,
            session_id=session_id,
            session_expiration_datetime=session_expiration_datetime,
        ),
        upsert=True,
    )


def delete(database: Database, session_id: SessionId) -> None:
    """Remove the session."""
    database.sessions.delete_one(dict(session_id=session_id))


def get(database, session_id):
    """Return the session object belonging to a session id."""
    return database.sessions.find_one({"session_id": session_id})
