"""Quality-time server."""

from gevent import monkey

monkey.patch_all()

# pylint: disable=wrong-import-order,wrong-import-position

import logging
import os  # skipcq: FLK-E402

import bottle  # skipcq: FLK-E402

from shared.initialization.database import init_database  # skipcq: FLK-E402

from initialization import init_bottle  # skipcq: FLK-E402


def serve() -> None:  # pragma: no cover-behave
    """Connect to the database and start the application server."""
    logging.getLogger().setLevel(logging.INFO)
    database = init_database()
    init_bottle(database)
    server_port = os.environ.get("EXTERNAL_SERVER_PORT", "5001")
    bottle.run(server="gevent", host="0.0.0.0", port=server_port, reloader=True, log=logging.getLogger())  # nosec


if __name__ == "__main__":  # pragma: no cover-behave
    serve()
