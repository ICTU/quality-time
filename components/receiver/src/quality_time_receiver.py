"""Quality-time receiver."""

from gevent import monkey  # pylint: disable=import-error
monkey.patch_all()

# pylint: disable=wrong-import-order,wrong-import-position

import bottle
import logging
import urllib
import os

from initialization import init_bottle, init_database


def receive() -> None:  # pragma: nocover
    """Connect to the database and start the measurements receiver."""
    logging.getLogger().setLevel(logging.INFO)
    database = init_database()
    init_bottle(database)
    receiver = urllib.parse.urlparse(os.environ.get("RECEIVER_URL", "http://localhost:5002"))  # type: ignore
    bottle.run(server="gevent", host="0.0.0.0", port=receiver.port, reloader=True, log=logging.getLogger())  # nosec


if __name__ == "__main__":
    receive()
