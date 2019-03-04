"""Login/logout."""

import re

import bottle


@bottle.post("/login")
def login(ldap_server=None):
    """Login the user."""
    credentials = dict(bottle.request.json)
    safe_characters = re.compile(r"\W+", re.UNICODE)
    username = re.sub(safe_characters, "", credentials.get("username", "no username given"))
    ldap_server.simple_bind_s(f"cn={username},dc=example,dc=org", credentials.get("password"))
    return dict(ok=True)
