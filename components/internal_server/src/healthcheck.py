"""Health check."""

from http import HTTPStatus
from os import getenv
from urllib.request import urlopen
import sys

internal_server_port = getenv("INTERNAL_SERVER_PORT", "5002")
# pylint: disable=invalid-name
exit_code = 1
try:
    with urlopen(f"http://localhost:{internal_server_port}/api/health") as response:  # nosec B310
        exit_code = 0 if response.status == HTTPStatus.OK else 1
finally:
    sys.exit(exit_code)
