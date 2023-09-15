"""Quality-time server."""

from gevent import monkey

monkey.patch_all()

import logging

import bottle

from shared.utils.env import getenv, loadenv

from initialization.database import init_database
from initialization.bottle import init_bottle


def serve() -> None:  # pragma: no feature-test-cover
    """Connect to the database and start the application server."""
    loadenv(".env", "default.env")
    log_level = getenv("API_SERVER_LOG_LEVEL")
    logger = logging.getLogger()
    logger.setLevel(log_level)
    database = init_database()
    init_bottle(database)
    server_port = getenv("API_SERVER_PORT")
    bottle.run(server="gevent", host="0.0.0.0", port=server_port, reloader=True, log=logger)  # nosec, # noqa: S104


if __name__ == "__main__":  # pragma: no feature-test-cover, pragma: no cover
    serve()
