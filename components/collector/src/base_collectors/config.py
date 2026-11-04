"""Configuration."""

import os
import pathlib
import tempfile

LOG_LEVEL = os.getenv("COLLECTOR_LOG_LEVEL", "WARNING")
HEALTH_CHECK_FILE = os.getenv("HEALTH_CHECK_FILE", str(pathlib.Path(tempfile.gettempdir()) / "health_check.txt"))
SLEEP_DURATION = int(os.getenv("COLLECTOR_SLEEP_DURATION", "20"))
MEASUREMENT_LIMIT = int(os.getenv("COLLECTOR_MEASUREMENT_LIMIT", "30"))
MEASUREMENT_FREQUENCY = int(os.getenv("COLLECTOR_MEASUREMENT_FREQUENCY", str(15 * 60)))
MEASUREMENT_TIMEOUT = int(os.getenv("COLLECTOR_MEASUREMENT_TIMEOUT", "120"))
# With the default values above, the collector starts at most 30 tasks every 20 seconds that time out after at most
# 120 seconds, so at most (120 / 20) * 30 = 180 tasks are running. The default threshold is 2/3 of that.
RUNNING_TASKS_HEALTHY_THRESHOLD = int(os.getenv("COLLECTOR_RUNNING_TASKS_HEALTHY_THRESHOLD", "120"))
