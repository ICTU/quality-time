"""Quality-time server."""

from gevent import monkey
monkey.patch_all()

# pylint: disable=wrong-import-order,wrong-import-position

import logging

import bottle

from . import cors  # pylint: disable=unused-import
from .routes import report, measurement, datamodel, auth  # pylint: disable=unused-import
from .initialization import init_bottle, init_database, init_ldap


def serve() -> None:  # pragma: nocover
    """Connect to the database and start the application server."""
    logging.getLogger().setLevel(logging.INFO)
    init_bottle()
    init_ldap()
    init_database()
    bottle.run(server="gevent", host='0.0.0.0', port=8080, reloader=True)
