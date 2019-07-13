"""LDAP initialization."""

import logging
import os

import bottle
import ldap  # pylint: disable=wrong-import-order,import-error

from ..route_plugins import InjectionPlugin


def init_ldap() -> None:
    """Initialize the LDAP connection."""
    ldap_url = os.environ.get("LDAP_URL", "ldap://localhost:389")
    logging.info("Initializing LDAP server at %s", ldap_url)
    ldap_server = ldap.initialize(ldap_url)
    ldap_injection_plugin = InjectionPlugin(value=ldap_server, keyword="ldap_server")
    bottle.install(ldap_injection_plugin)
