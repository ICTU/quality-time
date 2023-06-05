"""Configuration."""

import os

LOG_LEVEL = os.getenv("COLLECTOR_LOG_LEVEL", "WARNING")
HEALTH_CHECK_FILE = os.getenv("HEALTH_CHECK_FILE", "/home/collector/health_check.txt")
MAX_SLEEP_DURATION = int(os.getenv("COLLECTOR_SLEEP_DURATION", "20"))
MEASUREMENT_LIMIT = int(os.getenv("COLLECTOR_MEASUREMENT_LIMIT", "30"))
MEASUREMENT_FREQUENCY = int(os.getenv("COLLECTOR_MEASUREMENT_FREQUENCY", str(15 * 60)))
