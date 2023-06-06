"""Notifier."""

import asyncio
import logging
import os
from typing import NoReturn

from shared.initialization.database import database_connection

from notifier.notifier import notify


def start_notifications() -> NoReturn:
    """Notify indefinitely."""
    logging.getLogger().setLevel(str(os.getenv("NOTIFIER_LOG_LEVEL", "WARNING")))
    sleep_duration = int(os.getenv("NOTIFIER_SLEEP_DURATION", "60"))
    asyncio.run(notify(database_connection(), sleep_duration))


if __name__ == "__main__":  # pragma: no cover
    start_notifications()
