"""Login/logout."""

from datetime import datetime, timedelta
from typing import Dict
import logging
import os
import re
import urllib.parse

from pymongo.database import Database
import bottle
import ldap  # pylint: disable=import-error,wrong-import-order

from ..database import sessions
from ..util import uuid


def generate_session_id() -> str:
    """Generate a new random, secret and unique session id."""
    return uuid()


def set_session_cookie(session_id: str, clear: bool = False) -> None:
    """Set the session cookie on the response."""
    expires_datetime = datetime.min if clear else datetime.now() + timedelta(hours=24)
    options = dict(expires=expires_datetime, path="/", httponly=True)
    server_url = os.environ.get("SERVER_URL", "http://localhost:5001")
    domain = urllib.parse.urlparse(server_url).netloc.split(":")[0]
    if domain not in ("0.0.0.0", "localhost"):
        options["domain"] = domain
    bottle.response.set_cookie("session_id", session_id, **options)


@bottle.post("/login")
def login(database: Database, ldap_server) -> Dict[str, bool]:
    """Log the user in."""
    credentials = dict(bottle.request.json)
    unsafe_characters = re.compile(r"[^\w ]+", re.UNICODE)
    username = re.sub(unsafe_characters, "", credentials.get("username", "no username given"))
    ldap_root_dn = os.environ.get("LDAP_ROOT_DN", "dc=example,dc=org")
    try:
        ldap_server.simple_bind_s(f"cn={username},{ldap_root_dn}", credentials.get("password"))
    except (ldap.INVALID_CREDENTIALS, ldap.UNWILLING_TO_PERFORM, ldap.INVALID_DN_SYNTAX, ldap.SERVER_DOWN) as reason:  # pylint: disable=no-member
        logging.warning("Couldn't bind cn=%s,%s: %s", username, ldap_root_dn, reason)
        return dict(ok=False)
    session_id = generate_session_id()
    sessions.upsert(database, username, session_id)
    set_session_cookie(session_id)
    return dict(ok=True)


@bottle.post("/logout")
def logout(database: Database) -> Dict[str, bool]:
    """Log the user out."""
    session_id = str(bottle.request.get_cookie("session_id"))
    sessions.delete(database, session_id)
    set_session_cookie(session_id, clear=True)
    return dict(ok=True)
