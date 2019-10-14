"""Login/logout."""

from datetime import datetime, timedelta
import logging
import os
import re
from typing import Dict, Tuple
import urllib.parse

from pymongo.database import Database
import ldap3
from ldap3 import Server, Connection, ALL, NTLM, ObjectDef
from ldap3.core import exceptions
import bottle

from database import sessions
from utilities.functions import uuid
from utilities.ldap import LDAPObject


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
    # Pylint can't find the ldap.* constants for some reason, turn off the error message:
    # pylint: disable=no-member
    credentials = dict(bottle.request.json)
    unsafe_characters = re.compile(r"[^\w ]+", re.UNICODE)
    username = re.sub(unsafe_characters, "", credentials.get("username", "no username given"))
    password = credentials.get("password", "no password given")

    ldap_root_dn = os.environ.get("LDAP_ROOT_DN", "dc=example,dc=org")
    ldap_url = os.environ.get("LDAP_URL", "ldap://localhost:389")
    un_field = 'cn'

    # # these are params for devivmil oc ldap server
    # ldap_root_dn = "cn=users,cn=accounts,dc=oc,dc=devivmil,dc=ictu-sr,dc=nl"
    # ldap_url = "10.199.8.1" #"localhost"
    # un_field = 'uid'

    ldap_server = Server(ldap_url, get_info=ALL)
    try:
        with Connection(ldap_server, user=f"{un_field}={username},{ldap_root_dn}", password=password) as conn:
            if not conn.bind():
                logging.error("LDAP: bind error occurred: {}".format(conn.result))
                raise exceptions.LDAPBindError

    except (exceptions.LDAPInvalidCredentialsResult, exceptions.LDAPUnwillingToPerformResult, exceptions.LDAPInvalidDNSyntaxResult,
            exceptions.LDAPInvalidServerError, exceptions.LDAPServerPoolError, exceptions.LDAPServerPoolExhaustedError) as reason:
        logging.warning("Couldn't bind cn=%s,%s: %s", username, ldap_root_dn, reason)
        return dict(ok=False)
    except Exception as xreason:
        logging.warning("Couldn't bind cn=%s,%s: %s", username, ldap_root_dn, xreason)
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
