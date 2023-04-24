"""Notifier."""

import asyncio
import logging
import os

from notifier.notifier import notify

if __name__ == "__main__":  # pragma: no cover
    logging.getLogger().setLevel(str(os.getenv("NOTIFIER_LOG_LEVEL", "WARNING")))
    sleep_duration = int(os.getenv("NOTIFIER_SLEEP_DURATION", "60"))
    asyncio.run(notify(sleep_duration))
