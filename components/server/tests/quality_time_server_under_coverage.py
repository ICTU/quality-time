"""Quality-time server, with coverage measurement."""

import signal
import sys

import coverage


sys.path.insert(0, "src")

cov = coverage.Coverage()


def stop_coverage():
    """Stop and save the coverage."""
    if cov:
        cov.stop()
        cov.save()


def signal_handler(*args):  # pylint: disable=unused-argument
    """Save the coverage data on receiving a SIGTERM."""
    stop_coverage()
    sys.exit()


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)
    cov.start()
    from quality_time_server import serve

    try:
        serve()
    finally:
        stop_coverage()
