"""Login/logout."""

import os
import re
import string
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from http.cookies import Morsel
from typing import cast, TYPE_CHECKING

import argon2
import bottle
from dateutil.tz import tzutc
from ldap3 import ALL, Connection, Server, ServerPool, AUTO_BIND_NO_TLS
from ldap3.core import exceptions

from database.users import upsert_user, get_user
from database import sessions
from initialization.app_secrets import EXPORT_FIELDS_KEYS_NAME
from utils.functions import uuid
from utils.log import get_logger
from utils.type import SessionId, User

if TYPE_CHECKING:
    from pymongo.database import Database


def create_session(database: Database, user: User) -> datetime:
    """Create a new user session.

    Generate a new random, secret and unique session id and a session expiration datetime and add it to the
    database and the session cookie.
    """
    session_id = cast(SessionId, uuid())
    session_duration = int(os.getenv("USER_SESSION_DURATION", "120"))
    session_expiration_datetime = datetime.now(tzutc()) + timedelta(hours=session_duration)
    sessions.upsert(database, user, session_id, session_expiration_datetime)
    set_session_cookie(session_id, session_expiration_datetime)
    return session_expiration_datetime


def delete_session(database: Database) -> None:
    """Delete the session."""
    session_id = cast(SessionId, str(bottle.request.get_cookie("session_id")))
    sessions.delete(database, session_id)
    set_session_cookie(session_id, datetime.min.replace(tzinfo=tzutc()))


def set_session_cookie(session_id: SessionId, expires_datetime: datetime) -> None:
    """Set the session cookie on the response. To clear the cookie, pass an expiration datetime of datetime.min."""
    # Monkey patch support for SameSite, see https://github.com/bottlepy/bottle/issues/982#issuecomment-315064376
    Morsel._reserved["same-site"] = "SameSite"  # type: ignore[attr-defined] # noqa: SLF001
    options = {"expires": expires_datetime, "path": "/", "httponly": True, "same_site": "strict"}
    bottle.response.set_cookie("session_id", session_id, **options)


def check_password(password_hash, password) -> bool:
    """Check the OpenLDAP password hash against the given password."""
    # Note we currently only support ARGON2 hashes
    return argon2.PasswordHasher().verify(password_hash.decode().removeprefix("{ARGON2}"), password)


def get_credentials() -> tuple[str, str]:
    """Return the credentials from the request."""
    credentials = dict(bottle.request.json)
    unsafe_characters = re.compile(r"[^\w\- ]+", re.UNICODE)
    username = re.sub(unsafe_characters, "", credentials.get("username", "no username given"))
    password = credentials.get("password", "no password given")
    return username, password


@dataclass
class LDAPConfig:
    """LDAP configuration."""

    username: str
    root_dn: str = os.environ.get("LDAP_ROOT_DN", "dc=example,dc=org")
    urls: tuple[str, ...] = tuple(os.environ.get("LDAP_URL", "ldap://localhost:389").split(","))
    lookup_user_dn: str = os.environ.get("LDAP_LOOKUP_USER_DN", "cn=admin,dc=example,dc=org")
    lookup_user_pw: str = os.environ.get("LDAP_LOOKUP_USER_PASSWORD", "admin")
    search_filter: str = field(init=False)

    def __post_init__(self) -> None:
        """Instantiate the search filter with the username."""
        ldap_search_filter_template = os.environ.get("LDAP_SEARCH_FILTER", "(|(uid=$username)(cn=$username))")
        self.search_filter = string.Template(ldap_search_filter_template).substitute(username=self.username)


def verify_user(database: Database, username: str, password: str) -> User:
    """Authenticate the user and return whether they are authorized to login and their email address."""
    logger = get_logger()
    ldap = LDAPConfig(username)
    try:
        ldap_server_pool = ServerPool([Server(url, get_info=ALL) for url in ldap.urls])
        # Look up the user to authenticate, using the lookup-user credentials:
        with Connection(ldap_server_pool, user=ldap.lookup_user_dn, password=ldap.lookup_user_pw) as lookup_connection:
            if not lookup_connection.bind():  # pragma: no feature-test-cover
                raise exceptions.LDAPBindError  # noqa: TRY301
            lookup_connection.search(ldap.root_dn, ldap.search_filter, attributes=["userPassword", "cn", "mail"])
            ldap_user = lookup_connection.entries[0]
        # If the LDAP-server returned the user's password-hash, check the password against the hash, otherwise
        # attempt a bind operation using the user's distinguished name (dn) and password:
        if (password_hash := ldap_user.userPassword.value) and check_password(password_hash, password):
            logger.info("LDAP password check succeeded")
        else:  # pragma: no feature-test-cover
            with Connection(ldap_server_pool, user=ldap_user.entry_dn, password=password, auto_bind=AUTO_BIND_NO_TLS):
                logger.info("LDAP bind succeeded")
    except Exception as reason:  # noqa: BLE001
        user = User(username)
        logger.warning("LDAP error: %s", reason)
    else:
        user = get_user(database, username) or User(username)
        user.email = ldap_user.mail.value or ""
        user.common_name = ldap_user.cn.value
        user.verified = True
        upsert_user(database, user)
    return user


@bottle.post("/api/internal/login", authentication_required=False)
@bottle.post("/api/v3/login", authentication_required=False)
def login(database: Database) -> dict[str, bool | str]:
    """Log the user in. Add credentials as JSON payload, e.g. {username: 'user', password: 'pass'}."""
    if os.environ.get("FORWARD_AUTH_ENABLED", "").lower() == "true":  # pragma: no feature-test-cover
        forward_auth_header = str(os.environ.get("FORWARD_AUTH_HEADER", "X-Forwarded-User"))
        username = bottle.request.get_header(forward_auth_header, None)
        user = User(username, username or "", "", username is not None)
    else:
        username, password = get_credentials()
        user = verify_user(database, username, password)
    session_expiration_datetime = (
        create_session(database, user) if user.verified else datetime.min.replace(tzinfo=tzutc())
    )
    return {
        "ok": user.verified,
        "email": user.email,
        "session_expiration_datetime": session_expiration_datetime.isoformat(),
    }


@bottle.post("/api/internal/logout", authentication_required=True)
@bottle.post("/api/v3/logout", authentication_required=True)
def logout(database: Database) -> dict[str, bool]:
    """Log the user out."""
    delete_session(database)
    return {"ok": True}


@bottle.get("/api/v3/public_key", authentication_required=False)
def get_public_key(database: Database) -> dict:
    """Return a serialized version of the public key."""
    public_key = database.secrets.find_one({"name": EXPORT_FIELDS_KEYS_NAME}, {"public_key": True, "_id": False})
    return cast(dict, public_key)
