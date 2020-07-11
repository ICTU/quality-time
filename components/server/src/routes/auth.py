"""Login/logout."""

import base64
import hashlib
import logging
import os
import re
import string
from datetime import datetime, timedelta
from typing import cast, Dict, Tuple, Union

import bottle
from ldap3 import Server, Connection, ALL
from ldap3.core import exceptions
from pymongo.database import Database

from database import sessions
from server_utilities.functions import uuid
from server_utilities.type import SessionId


def create_session(database: Database, username: str, email: str) -> None:
    """Generate a new random, secret and unique session id and a session expiration datetime and add it to the
    database and the session cookie."""
    session_id = cast(SessionId, uuid())
    session_expiration_datetime = datetime.now() + timedelta(hours=24)
    sessions.upsert(database, username, email, session_id, session_expiration_datetime)
    set_session_cookie(session_id, session_expiration_datetime)


def delete_session(database: Database) -> None:
    """Delete the session."""
    session_id = cast(SessionId, str(bottle.request.get_cookie("session_id")))
    sessions.delete(database, session_id)
    set_session_cookie(session_id, datetime.min)


def set_session_cookie(session_id: SessionId, expires_datetime: datetime) -> None:
    """Set the session cookie on the response. To clear the cookie, pass an expiration datetime of datetime.min."""
    options = dict(expires=expires_datetime, path="/", httponly=True)
    bottle.response.set_cookie("session_id", session_id, **options)


def check_password(ssha_ldap_salted_password, password):
    """Checks the OpenLDAP tagged digest against the given password"""

    if ssha_ldap_salted_password[:6] != b'{SSHA}':
        logging.warning("Only SSHA LDAP password digest supported!")
        raise exceptions.LDAPInvalidAttributeSyntaxResult

    digest_salt_b64 = ssha_ldap_salted_password[6:]  # strip {SSHA}
    digest_salt = base64.b64decode(digest_salt_b64)
    digest = digest_salt[:20]
    salt = digest_salt[20:]
    sha = hashlib.sha1(bytes(password, 'utf-8'))  # nosec
    sha.update(salt)  # nosec
    return digest == sha.digest()


def get_credentials() -> Tuple[str, str]:
    """Return the credentials from the request."""
    credentials = dict(bottle.request.json)
    unsafe_characters = re.compile(r"[^\w\- ]+", re.UNICODE)
    username = re.sub(unsafe_characters, "", credentials.get("username", "no username given"))
    password = credentials.get("password", "no password given")
    return username, password


def verify_user(username: str, password: str) -> Tuple[bool, str]:
    """Authenticate the user and return whether they are authorized to login and their email address."""
    def user(username: str, email: str) -> str:
        """Format user and email for logging purposes."""
        return f"user {username} <{email or 'unknown email'}>"

    ldap_root_dn = os.environ.get("LDAP_ROOT_DN", "dc=example,dc=org")
    ldap_url = os.environ.get("LDAP_URL", "ldap://localhost:389")
    ldap_lookup_user_dn = os.environ.get("LDAP_LOOKUP_USER_DN", "cn=admin,dc=example,dc=org")
    ldap_lookup_user_password = os.environ.get("LDAP_LOOKUP_USER_PASSWORD", "admin")
    ldap_search_filter_template = os.environ.get("LDAP_SEARCH_FILTER", "(|(uid=$username)(cn=$username))")
    ldap_search_filter = string.Template(ldap_search_filter_template).substitute(username=username)
    email = ""
    try:
        ldap_server = Server(ldap_url, get_info=ALL)
        with Connection(ldap_server, user=ldap_lookup_user_dn, password=ldap_lookup_user_password) as lookup_connection:
            if not lookup_connection.bind():
                username = ldap_lookup_user_dn
                raise exceptions.LDAPBindError
            lookup_connection.search(ldap_root_dn, ldap_search_filter, attributes=['userPassword', 'mail'])
            result = lookup_connection.entries[0]
        username, salted_password = result.entry_dn, result.userPassword.value
        email = result.mail.value or ""
        if salted_password:
            if check_password(salted_password, password):
                logging.info("LDAP salted password check for %s succeeded", user(username, email))
            else:
                raise exceptions.LDAPInvalidCredentialsResult
        else:
            with Connection(ldap_server, user=username, password=password, auto_bind=True):
                logging.info("LDAP bind for %s succeeded", user(username, email))
    except Exception as reason:  # pylint: disable=broad-except
        logging.warning("LDAP error for %s: %s", user(username, email), reason)
        return False, email
    return True, email


@bottle.post("/api/v3/login")
def login(database: Database) -> Dict[str, Union[bool, str]]:
    """Log the user in. Add credentials as JSON payload, e.g. {username: 'user', password: 'pass'}."""
    username, password = get_credentials()
    verified, email = verify_user(username, password)
    if verified:
        create_session(database, username, email)
    return dict(ok=verified, email=email)


@bottle.post("/api/v3/logout")
def logout(database: Database) -> Dict[str, bool]:
    """Log the user out."""
    delete_session(database)
    return dict(ok=True)
