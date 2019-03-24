"""Login/logout."""

from datetime import datetime, timedelta
import os
import re
import urllib.parse

import bottle

from ..database import sessions
from ..util import uuid


def set_session_cookie(session_id: str, clear: bool = False):
    """Set the session cookie on the response."""
    expires_datetime = datetime.min if clear else datetime.now() + timedelta(hours=24)
    server_url = os.environ.get("SERVER_URL", "http://localhost:8080")
    domain = urllib.parse.urlparse(server_url).netloc.split(":")[0]
    bottle.response.set_cookie(
        "session_id", session_id, expires=expires_datetime, domain=domain, path="/", httponly=True)


@bottle.post("/login")
def login(database, ldap_server=None):
    """Log the user in."""
    credentials = dict(bottle.request.json)
    safe_characters = re.compile(r"\W+", re.UNICODE)
    username = re.sub(safe_characters, "", credentials.get("username", "no username given"))
    ldap_server.simple_bind_s(f"cn={username},dc=example,dc=org", credentials.get("password"))
    session_id = uuid()
    sessions.upsert(database, username, session_id)
    set_session_cookie(session_id)
    return dict(ok=True)


@bottle.post("/logout")
def logout(database):
    """Log the user out."""
    session_id = bottle.request.get_cookie("session_id")
    sessions.delete(database, session_id)
    set_session_cookie(session_id, clear=True)
    return dict(ok=True)
