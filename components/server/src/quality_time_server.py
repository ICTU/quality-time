"""Quality-time server."""
import os  # skipcq: FLK-E402
import sys

print(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../shared_python")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../shared_python")))

from gevent import monkey  # pylint: disable=import-error

monkey.patch_all()

# pylint: disable=wrong-import-order,wrong-import-position

import logging

# import os  # skipcq: FLK-E402

import bottle  # skipcq: FLK-E402

from external.initialization.database import init_database  # skipcq: FLK-E402
from shared.initialization import init_bottle  # skipcq: FLK-E402


def serve() -> None:  # pragma: no cover-behave
    """Connect to the database and start the application server."""
    logging.getLogger().setLevel(logging.INFO)
    database = init_database()
    init_bottle(database)
    server_port = os.environ.get("SERVER_PORT", "5001")
    bottle.run(server="gevent", host="0.0.0.0", port=server_port, reloader=True, log=logging.getLogger())  # nosec


if __name__ == "__main__":  # pragma: no cover-behave
    serve()
