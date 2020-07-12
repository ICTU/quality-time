"""Quality-time server."""

from gevent import monkey  # pylint: disable=import-error
monkey.patch_all()

import coverage
cov = coverage.process_startup()

# pylint: disable=wrong-import-order,wrong-import-position

import signal

from quality_time_server import serve


def signal_handler(*args):
    if cov:
        cov.save()


if __name__ == "__main__":  # pragma: no cover-behave
    signal.signal(signal.SIGTERM, signal_handler)
    serve()
