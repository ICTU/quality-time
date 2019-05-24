"""Sessions collection."""

from pymongo.database import Database

from ..util import iso_timestamp


def upsert(database: Database, username: str, session_id: str) -> None:
    """Update the existing session for the user or insert a new session."""
    database.sessions.update(
        dict(user=username), dict(user=username, timestamp=iso_timestamp(), session_id=session_id), upsert=True)


def delete(database: Database, session_id: str) -> None:
    """Remove the session."""
    database.sessions.delete_one(dict(session_id=session_id))


def valid(database: Database, session_id: str) -> bool:
    """Return whether the session is present in the database."""
    return database.sessions.find_one(dict(session_id=session_id)) is not None
