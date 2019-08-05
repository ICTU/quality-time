"""Quality-time server."""

import os

DEBUG = os.environ.get("DEBUG", "").lower() == "true"

if not DEBUG:
    from gevent import monkey  # pylint: disable=import-error
    monkey.patch_all()

# pylint: disable=wrong-import-order,wrong-import-position

import bottle
import logging
import urllib

from initialization import init_bottle, init_database


def serve() -> None:  # pragma: nocover
    """Connect to the database and start the application server."""
    logging.getLogger().setLevel(logging.INFO)
    database = init_database()
    init_bottle(database)
    server = urllib.parse.urlparse(os.environ.get("SERVER_URL_EXTERNAL", "http://localhost:5001"))
    bottle.run(  # nosec
        server="wsgiref" if DEBUG else "gevent", host="0.0.0.0", port=server.port, reloader=not DEBUG,
        log=None if DEBUG else logging.getLogger())


if __name__ == "__main__":
    serve()
