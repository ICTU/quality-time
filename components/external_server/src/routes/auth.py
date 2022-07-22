"""Login/logout."""

import base64
import hashlib
import logging
import os
import re
import string
from datetime import datetime, timedelta, timezone
from http.cookies import Morsel
from typing import cast

import bottle
from ldap3 import ALL, Connection, Server, ServerPool, AUTO_BIND_NO_TLS
from ldap3.core import exceptions
from pymongo.database import Database

from shared.initialization.secrets import EXPORT_FIELDS_KEYS_NAME
from shared.utils.type import SessionId, User

from database.users import upsert_user, get_user
from database import sessions
from utils.functions import uuid


def create_session(database: Database, user: User) -> datetime:
    """Create a new user session.

    Generate a new random, secret and unique session id and a session expiration datetime and add it to the
    database and the session cookie.
    """
    session_id = cast(SessionId, uuid())
    session_expiration_datetime = datetime.now(timezone.utc) + timedelta(hours=24)
    sessions.upsert(database, user, session_id, session_expiration_datetime)
    set_session_cookie(session_id, session_expiration_datetime)
    return session_expiration_datetime


def delete_session(database: Database) -> None:
    """Delete the session."""
    session_id = cast(SessionId, str(bottle.request.get_cookie("session_id")))
    sessions.delete(database, session_id)
    set_session_cookie(session_id, datetime.min)


def set_session_cookie(session_id: SessionId, expires_datetime: datetime) -> None:
    """Set the session cookie on the response. To clear the cookie, pass an expiration datetime of datetime.min."""
    # Monkey patch support for SameSite, see https://github.com/bottlepy/bottle/issues/982#issuecomment-315064376
    Morsel._reserved["same-site"] = "SameSite"  # type: ignore  # pylint: disable=protected-access
    options = dict(expires=expires_datetime, path="/", httponly=True, same_site="strict")
    bottle.response.set_cookie("session_id", session_id, **options)


def check_password(ssha_ldap_salted_password, password) -> bool:
    """Check the OpenLDAP tagged digest against the given password."""
    # See https://www.openldap.org/doc/admin24/security.html#SSHA%20password%20storage%20scheme
    # We should (also) support SHA512 as SHA1 is no longer considered to be secure.
    ssha_prefix = b"{SSHA}"
    if not ssha_ldap_salted_password.startswith(ssha_prefix):  # pragma: no cover-behave
        logging.warning("Only SSHA LDAP password digest supported!")
        raise exceptions.LDAPInvalidAttributeSyntaxResult
    digest_salt_b64 = ssha_ldap_salted_password.removeprefix(ssha_prefix)
    digest_salt = base64.b64decode(digest_salt_b64)
    digest = digest_salt[:20]
    salt = digest_salt[20:]
    sha = hashlib.sha1(bytes(password, "utf-8"))  # noqa: DUO130, # nosec
    sha.update(salt)  # nosec
    return digest == sha.digest()


def get_credentials() -> tuple[str, str]:
    """Return the credentials from the request."""
    credentials = dict(bottle.request.json)
    unsafe_characters = re.compile(r"[^\w\- ]+", re.UNICODE)
    username = re.sub(unsafe_characters, "", credentials.get("username", "no username given"))
    password = credentials.get("password", "no password given")
    return username, password


def get_ldap_config(username):
    """Get LDAP config from environment."""
    ldap_search_filter_template = os.environ.get("LDAP_SEARCH_FILTER", "(|(uid=$username)(cn=$username))")
    ldap_config = dict(
        ldap_root_dn=os.environ.get("LDAP_ROOT_DN", "dc=example,dc=org"),
        ldap_urls=os.environ.get("LDAP_URL", "ldap://localhost:389").split(","),
        ldap_lookup_user_dn=os.environ.get("LDAP_LOOKUP_USER_DN", "cn=admin,dc=example,dc=org"),
        ldap_lookup_user_pw=os.environ.get("LDAP_LOOKUP_USER_PASSWORD", "admin"),
        ldap_search_filter=string.Template(ldap_search_filter_template).substitute(username=username),
    )
    return ldap_config


def verify_user(database: Database, username: str, password: str) -> User:
    """Authenticate the user and return whether they are authorized to login and their email address."""
    ldap_config = get_ldap_config(username)
    try:
        ldap_servers = [Server(ldap_url, get_info=ALL) for ldap_url in ldap_config.get("ldap_urls")]
        ldap_server_pool = ServerPool(ldap_servers)
        with Connection(
            ldap_server_pool,
            user=ldap_config.get("ldap_lookup_user_dn"),
            password=ldap_config.get("ldap_lookup_user_pw"),
        ) as lookup_connection:
            if not lookup_connection.bind():  # pragma: no cover-behave
                raise exceptions.LDAPBindError
            lookup_connection.search(
                ldap_config.get("ldap_root_dn"),
                ldap_config.get("ldap_search_filter"),
                attributes=["userPassword", "cn", "mail"],
            )
            result = lookup_connection.entries[0]
        if salted_password := result.userPassword.value:
            if check_password(salted_password, password):
                logging.info("LDAP salted password check for %s succeeded", username)
            else:
                raise exceptions.LDAPInvalidCredentialsResult
        else:  # pragma: no cover-behave
            with Connection(ldap_server_pool, user=result.entry_dn, password=password, auto_bind=AUTO_BIND_NO_TLS):
                logging.info("LDAP bind for %s succeeded", username)
    except Exception as reason:  # pylint: disable=broad-except
        user = User(username)
        logging.warning("LDAP error: %s", reason)
    else:
        user = get_user(database, username)
        user.email = result.mail.value or ""
        user.common_name = result.cn.value
        user.verified = True
        upsert_user(database, user)
    return user


@bottle.post("/api/v3/login", authentication_required=False)
def login(database: Database) -> dict[str, bool | str]:
    """Log the user in. Add credentials as JSON payload, e.g. {username: 'user', password: 'pass'}."""
    if os.environ.get("FORWARD_AUTH_ENABLED", "").lower() == "true":  # pragma: no cover-behave
        forward_auth_header = str(os.environ.get("FORWARD_AUTH_HEADER", "X-Forwarded-User"))
        username = bottle.request.get_header(forward_auth_header, None)
        user = User(username, username or "", "", username is not None)
    else:
        username, password = get_credentials()
        user = verify_user(database, username, password)
    if user.verified:
        session_expiration_datetime = create_session(database, user)
    else:
        session_expiration_datetime = datetime.min.replace(tzinfo=timezone.utc)
    return dict(ok=user.verified, email=user.email, session_expiration_datetime=session_expiration_datetime.isoformat())


@bottle.post("/api/v3/logout", authentication_required=True)
def logout(database: Database) -> dict[str, bool]:
    """Log the user out."""
    delete_session(database)
    return dict(ok=True)


@bottle.get("/api/v3/public_key", authentication_required=False)
def get_public_key(database: Database) -> dict:
    """Return a serialized version of the public key."""
    public_key = database.secrets.find_one({"name": EXPORT_FIELDS_KEYS_NAME}, {"public_key": True, "_id": False})
    public_key_as_dict = cast(dict, public_key)
    return public_key_as_dict
