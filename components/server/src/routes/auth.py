"""Login/logout."""

from datetime import datetime, timedelta
import logging
import os
import re
from typing import Dict, Tuple
import urllib.parse

from pymongo.database import Database
from ldap3 import Server, Connection, ALL
from ldap3.core import exceptions
import bottle
import hashlib
import base64

from database import sessions
from utilities.functions import uuid


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

def check_password(ssha_ldap_salted_password, password):
    """Checks the OpenLDAP tagged digest against the given password"""

    digest_salt_b64 = ssha_ldap_salted_password[6:]  # strip {SSHA}

    digest_salt = base64.b64decode(digest_salt_b64)
    digest = digest_salt[:20]
    salt = digest_salt[20:]

    sha = hashlib.sha1(bytes(password, 'utf-8'))
    sha.update(salt)

    return digest == sha.digest()

@bottle.post("/login")
def login(database: Database) -> Dict[str, bool]:
    """Log the user in."""
    credentials = dict(bottle.request.json)
    unsafe_characters = re.compile(r"[^\w ]+", re.UNICODE)
    username = re.sub(unsafe_characters, "", credentials.get("username", "no username given"))
    ldap_root_dn = os.environ.get("LDAP_ROOT_DN", "dc=example,dc=org")
    ldap_url = os.environ.get("LDAP_URL", "ldap://localhost:389")
    ldap_lookup_user = os.environ.get("LDAP_LOOKUP_USER", "admin")
    ldap_lookup_user_password = os.environ.get("LDAP_LOOKUP_USER_PASSWORD", "admin")

    try:
        ldap_server = Server(ldap_url, get_info=ALL)
        with Connection(ldap_server, user=f"cn={ldap_lookup_user},{ldap_root_dn}", password=ldap_lookup_user_password) as conn:
            if not conn.bind():
                username = ldap_lookup_user
                raise exceptions.LDAPBindError

            conn.search(ldap_root_dn, f"(|(uid={username})(cn={username}))", attributes=['userPassword']) # ALL_ATTRIBUTES
            result = conn.entries[0]
            # if not result.userPassword:
            #     raise exceptions.LDAPInvalidAttributeSyntaxResult

            password = credentials.get("password", "no password given")
            if not check_password(result.userPassword.value, password):
                return dict(ok=False)

    except Exception as reason:
        logging.warning("LDAP error for cn=%s,%s: %s", username, ldap_root_dn, reason)
        return dict(ok=False)

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
