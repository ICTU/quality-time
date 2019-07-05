"""Quality-time server."""

from gevent import monkey  # pylint: disable=import-error
monkey.patch_all()

# pylint: disable=wrong-import-order,wrong-import-position

import logging
import urllib
import os

import bottle

from . import cors  # pylint: disable=unused-import
from .routes import report, measurement, datamodel, auth  # pylint: disable=unused-import
from .initialization import init_bottle, init_database, init_ldap


def serve() -> None:  # pragma: nocover
    """Connect to the database and start the application server."""
    logging.getLogger().setLevel(logging.INFO)
    init_ldap()
    init_database()
    init_bottle()
    server = urllib.parse.urlparse(os.environ.get("SERVER_URL", "http://localhost:5001"))
    reload = server.hostname == "localhost"
    bottle.run(server="gevent", host=server.hostname, port=server.port, reloader=reload, log=logging.getLogger())
