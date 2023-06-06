"""Notifier."""

import asyncio
import logging
import os

from shared.initialization.database import database_connection  # pragma: no cover

from notifier.notifier import notify

if __name__ == "__main__":  # pragma: no cover
    logging.getLogger().setLevel(str(os.getenv("NOTIFIER_LOG_LEVEL", "WARNING")))  # pragma: no cover
    sleep_duration = int(os.getenv("NOTIFIER_SLEEP_DURATION", "60"))  # pragma: no cover
    asyncio.run(notify(database_connection(), sleep_duration))  # pragma: no cover
