"""Health check."""

import os
import sys
from http import HTTPStatus
from urllib.request import urlopen

api_server_port = os.environ["API_SERVER_PORT"]
exit_code = 1
try:
    with urlopen(f"http://localhost:{api_server_port}/api/health") as response:  # nosec B310 # noqa: S310
        exit_code = 0 if response.status == HTTPStatus.OK else 1
finally:
    sys.exit(exit_code)
