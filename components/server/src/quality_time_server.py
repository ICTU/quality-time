"""Quality-time server."""

# isort: off
from gevent import monkey  # pylint: disable=import-error

monkey.patch_all()

# isort: on
# pylint: disable=wrong-import-order,wrong-import-position

import logging
import os  # skipcq: FLK-E402

import bottle  # skipcq: FLK-E402

from initialization import init_bottle, init_database  # skipcq: FLK-E402


def serve() -> None:  # pragma: no cover-behave
    """Connect to the database and start the application server."""
    logging.getLogger().setLevel(logging.INFO)
    database = init_database()
    init_bottle(database)
    server_port = os.environ.get("SERVER_PORT", "5001")
    bottle.run(server="gevent", host="0.0.0.0", port=server_port, reloader=True, log=logging.getLogger())  # nosec


if __name__ == "__main__":  # pragma: no cover-behave
    serve()
