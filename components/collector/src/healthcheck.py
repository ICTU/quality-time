"""Health check."""

import os
import pathlib
import sys
import tempfile
from datetime import UTC, datetime, timedelta

health_check_file = os.getenv("HEALTH_CHECK_FILE", str(tempfile.gettempdir() + "/health_check.txt"))
exit_code = 1
try:
    timestamp = pathlib.Path(health_check_file).read_text().strip()
    last_healthy = datetime.fromisoformat(timestamp)
    exit_code = 0 if datetime.now(tz=UTC) - last_healthy <= timedelta(seconds=600) else 1
finally:
    sys.exit(exit_code)
