"""Health check."""

from http import HTTPStatus
from os import getenv
from urllib.request import urlopen
import sys

external_server_port = getenv("EXTERNAL_SERVER_PORT", "5001")
# pylint: disable=invalid-name
exit_code = 1
try:
    with urlopen(f"http://localhost:{external_server_port}/api/health") as response:  # nosec B310 # noqa: S310
        exit_code = 0 if response.status == HTTPStatus.OK else 1
finally:
    sys.exit(exit_code)
