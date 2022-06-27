"""Define all routes about settings."""
from typing import cast
import bottle
from pymongo.database import Database
from shared.utils.type import SessionId, User

from database.sessions import get
from database.users import upsert_user, get_user


def find_user(database: Database) -> User:
    """Find the user belonging to a session_id"""
    session_id = cast(SessionId, str(bottle.request.get_cookie("session_id")))
    session = get(database, session_id)
    username = session.get("user")
    user = get_user(database, username)
    return user


@bottle.get("/api/v3/settings", authentication_required=True)
def get_settings(database: Database) -> dict:
    """Retrieve settings for user."""
    user = find_user(database)
    return dict(settings=user.settings)


@bottle.post("/api/v3/settings/update", authentication_required=True)
def update_settings(database: Database) -> dict[str, bool]:
    """Update the settings for the logged-in user."""
    new_settings = dict(bottle.request.json)
    user = find_user(database)
    user.settings = new_settings
    upsert_user(database, user)
    return dict(ok=True)
