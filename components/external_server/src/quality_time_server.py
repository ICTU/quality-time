"""Quality-time server."""

from gevent import monkey

monkey.patch_all()

# pylint: disable=wrong-import-order,wrong-import-position

import logging
import os  # skipcq: FLK-E402
from typing import NoReturn

import bottle  # skipcq: FLK-E402

from shared.initialization.database import init_database  # skipcq: FLK-E402

from initialization import init_bottle  # skipcq: FLK-E402


def serve() -> NoReturn:  # pragma: no feature-test-cover
    """Connect to the database and start the application server."""
    log_level = str(os.getenv("EXTERNAL_SERVER_LOG_LEVEL", "WARNING"))
    logging.getLogger().setLevel(log_level)
    database = init_database()
    init_bottle(database)
    server_port = os.getenv("EXTERNAL_SERVER_PORT", "5001")
    bottle.run(server="gevent", host="0.0.0.0", port=server_port, reloader=True, log=logging.getLogger())  # nosec


if __name__ == "__main__":  # pragma: no feature-test-cover
    serve()
