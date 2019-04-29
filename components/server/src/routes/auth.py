"""Login/logout."""

from datetime import datetime, timedelta
import os
import re
import urllib.parse

from pymongo.database import Database
import bottle
import ldap

from ..database import sessions
from ..util import uuid


def set_session_cookie(session_id: str, clear: bool = False) -> None:
    """Set the session cookie on the response."""
    expires_datetime = datetime.min if clear else datetime.now() + timedelta(hours=24)
    server_url = os.environ.get("SERVER_URL", "http://localhost:8080")
    domain = urllib.parse.urlparse(server_url).netloc.split(":")[0]
    bottle.response.set_cookie(
        "session_id", session_id, expires=expires_datetime, domain=domain, path="/", httponly=True)


@bottle.post("/login")
def login(database: Database, ldap_server):
    """Log the user in."""
    credentials = dict(bottle.request.json)
    safe_characters = re.compile(r"\W+", re.UNICODE)
    username = re.sub(safe_characters, "", credentials.get("username", "no username given"))
    try:
        ldap_server.simple_bind_s(f"cn={username},dc=example,dc=org", credentials.get("password"))
    except (ldap.INVALID_CREDENTIALS, ldap.UNWILLING_TO_PERFORM, ldap.INVALID_DN_SYNTAX):
        return dict(ok=False)
    session_id = uuid()
    sessions.upsert(database, username, session_id)
    set_session_cookie(session_id)
    return dict(ok=True)


@bottle.post("/logout")
def logout(database: Database):
    """Log the user out."""
    session_id = str(bottle.request.get_cookie("session_id"))
    sessions.delete(database, session_id)
    set_session_cookie(session_id, clear=True)
    return dict(ok=True)
