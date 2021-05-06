"""Quality-time server, with coverage measurement."""

import sys

import coverage


sys.path.insert(0, "src")


if __name__ == "__main__":
    cov = coverage.Coverage()
    cov.start()
    from quality_time_server import serve

    try:
        serve()
    finally:
        cov.stop()
        cov.save()
