"""Quality-time server."""

# pylint: disable=wrong-import-order,wrong-import-position

import signal
import sys

# isort: off

import coverage

cov = coverage.process_startup()

sys.path.insert(0, "src")
from quality_time_server import serve

# isort: on


def signal_handler(*args):  # pylint: disable=unused-argument
    """Save the coverage data on receiving a SIGTERM."""
    if cov:
        cov.save()
    sys.exit()


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)
    serve("wsgiref")
