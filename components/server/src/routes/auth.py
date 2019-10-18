"""Login/logout."""

from datetime import datetime, timedelta
import logging
import os
import re
from typing import cast, Dict, Tuple
import urllib.parse

from pymongo.database import Database
import ldap
import bottle

from database import sessions
from utilities.functions import uuid
from utilities.ldap import LDAPObject
from utilities.type import SessionId


def generate_session() -> Tuple[SessionId, datetime]:
    """Generate a new random, secret and unique session id and a session expiration datetime."""
    return cast(SessionId, uuid()), datetime.now() + timedelta(hours=24)


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
    # Pylint can't find the ldap.* constants for some reason, turn off the error message:
    # pylint: disable=no-member
    credentials = dict(bottle.request.json)
    unsafe_characters = re.compile(r"[^\w ]+", re.UNICODE)
    username = re.sub(unsafe_characters, "", credentials.get("username", "no username given"))
    ldap_root_dn = os.environ.get("LDAP_ROOT_DN", "dc=example,dc=org")
    ldap_url = os.environ.get("LDAP_URL", "ldap://localhost:389")
    ldap_lookup_user = os.environ.get("LDAP_LOOKUP_USER", "admin")
    ldap_lookup_user_password = os.environ.get("LDAP_LOOKUP_USER_PASSWORD", "admin")
    ldap_server = ldap.initialize(ldap_url)
    try:
        ldap_server.simple_bind_s(f"cn={ldap_lookup_user},{ldap_root_dn}", ldap_lookup_user_password)
        result = ldap_server.search_s(
            ldap_root_dn, ldap.SCOPE_SUBTREE, f"(|(uid={username})(cn={username}))", ['dn', 'uid', 'cn'])
        if result:
            logging.info("LDAP search result: %s", result)
            username = LDAPObject(result[0][1]).cn
        else:
            raise ldap.INVALID_CREDENTIALS
        ldap_server.simple_bind_s(f"cn={username},{ldap_root_dn}", credentials.get("password"))
    except (ldap.INVALID_CREDENTIALS, ldap.UNWILLING_TO_PERFORM, ldap.INVALID_DN_SYNTAX,
            ldap.SERVER_DOWN) as reason:
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
    session_id = cast(SessionId, str(bottle.request.get_cookie("session_id")))
    sessions.delete(database, session_id)
    set_session_cookie(session_id, datetime.min)
    return dict(ok=True)
