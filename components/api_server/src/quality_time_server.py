"""Quality-time server."""

from gevent import monkey

monkey.patch_all()

import logging
import os

from bottle import run

from shared.initialization.database import get_database, mongo_client

from initialization.database import init_database, set_feature_compatibility_version
from initialization.bottle import init_bottle


def serve() -> None:  # pragma: no feature-test-cover
    """Connect to the database and start the application server."""
    log_level = str(os.getenv("API_SERVER_LOG_LEVEL", "WARNING"))
    logger = logging.getLogger()
    logger.setLevel(log_level)
    with mongo_client() as client:
        admin_database = get_database(client, "admin")
        set_feature_compatibility_version(admin_database)
        database = get_database(client)
        init_database(database)
        init_bottle(database)
        server_port = int(os.getenv("API_SERVER_PORT", "5001"))
        run(server="gevent", host="0.0.0.0", port=server_port, reloader=True, log=logger)  # nosec, # noqa: S104


if __name__ == "__main__":  # pragma: no feature-test-cover, pragma: no cover
    serve()
