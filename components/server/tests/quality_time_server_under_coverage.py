"""Quality-time server, with coverage measurement."""

import sys

import coverage

sys.path.insert(0, "src")
from quality_time_server import serve


if __name__ == "__main__":
    cov = coverage.Coverage()
    cov.start()
    try:
        serve()
    finally:
        cov.stop()
        cov.save()
