"""Sessions collection."""

from ..util import iso_timestamp


def upsert(database, username: str, session_id: str) -> None:
    """Update the existing session for the user or insert a new session."""
    database.sessions.update(
        dict(user=username), dict(user=username, timestamp=iso_timestamp(), session_id=session_id), upsert=True)


def delete(database, session_id: str) -> None:
    """Remove the session."""
    database.sessions.delete_one(dict(session_id=session_id))
