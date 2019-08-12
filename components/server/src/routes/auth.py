"""Login/logout."""

import logging
import os
import re
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, Tuple

import bottle
import ldap  # pylint: disable=import-error,wrong-import-order
from pymongo.database import Database

from utilities.functions import uuid
from database import sessions
from utilities.ldap import LDAPUserObject


def generate_session() -> Tuple[str, datetime]:
    """Generate a new random, secret and unique session id and a session expiration datetime."""
    return uuid(), datetime.now() + timedelta(hours=24)


def set_session_cookie(session_id: str, expires_datetime: datetime) -> None:
    """Set the session cookie on the response. To clear the cookie, pass an expiration datetime of datetime.min."""
    options = dict(expires=expires_datetime, path="/", httponly=True)
    server_url = os.environ.get("SERVER_URL", "http://localhost:5001")
    domain = urllib.parse.urlparse(server_url).netloc.split(":")[0]
    if domain != "localhost":
        options["domain"] = domain
    bottle.response.set_cookie("session_id", session_id, **options)


@bottle.post("/login")
def login(database: Database) -> Dict[str, bool]:
    """Log the user in."""
    credentials = dict(bottle.request.json)
    unsafe_characters = re.compile(r"[^\w ]+", re.UNICODE)
    username = re.sub(unsafe_characters, "", credentials.get("username", "no username given"))

    ldap_root_dn = os.environ.get("LDAP_ROOT_DN", "dc=example,dc=org")

    ldap_lookup_user = os.environ.get("LDAP_LOOKUP_USER", "admin")
    ldap_lookup_user_password = os.environ.get("LDAP_LOOKUP_USER_PASSWORD", "admin")

    ldap_url = os.environ.get("LDAP_URL", "ldap://localhost:389")
    ldap_server = ldap.initialize(ldap_url)

    try:
        ldap_server.simple_bind_s(f"cn={ldap_lookup_user},{ldap_root_dn}", ldap_lookup_user_password)
    except (ldap.INVALID_CREDENTIALS, ldap.UNWILLING_TO_PERFORM, ldap.INVALID_DN_SYNTAX, ldap.SERVER_DOWN) as reason:  # pylint: disable=no-member
        logging.warning("Couldn't bind cn=%s,%s: %s", username, ldap_root_dn, reason)
        return dict(ok=False)

    try:
        result = ldap_server.search_s(
            ldap_root_dn, ldap.SCOPE_SUBTREE, f"(|(uid={username})(cn={username}))", ['dn', 'uid', 'cn']
        )
        if result:
            username = LDAPUserObject(result[0]).cn
        else:
            raise ldap.INVALID_CREDENTIALS
    except (ldap.INVALID_CREDENTIALS, ldap.UNWILLING_TO_PERFORM, ldap.INVALID_DN_SYNTAX, ldap.SERVER_DOWN) as reason:  # pylint: disable=no-member
        logging.warning("Couldn't bind cn=%s,%s: %s", username, ldap_root_dn, reason)
        return dict(ok=False)

    try:
        ldap_server.simple_bind_s(f"cn={username},{ldap_root_dn}", credentials.get("password"))
    except (ldap.INVALID_CREDENTIALS, ldap.UNWILLING_TO_PERFORM, ldap.INVALID_DN_SYNTAX, ldap.SERVER_DOWN) as reason:  # pylint: disable=no-member
        logging.warning("Couldn't bind cn=%s,%s: %s", username, ldap_root_dn, reason)
        return dict(ok=False)
    finally:
        ldap_server.unbind_s()

    session_id, session_expiration_datetime = generate_session()
    sessions.upsert(database, username, session_id, session_expiration_datetime)
    set_session_cookie(session_id, session_expiration_datetime)
    return dict(ok=True)


@bottle.post("/logout")
def logout(database: Database) -> Dict[str, bool]:
    """Log the user out."""
    session_id = str(bottle.request.get_cookie("session_id"))
    sessions.delete(database, session_id)
    set_session_cookie(session_id, datetime.min)
    return dict(ok=True)
