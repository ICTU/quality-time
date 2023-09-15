"""Notifier."""

import asyncio
import logging
from typing import NoReturn

from shared.initialization.database import database_connection
from shared.utils.env import getenv

from notifier.notifier import notify


def start_notifications() -> NoReturn:
    """Notify indefinitely."""
    logging.getLogger().setLevel(getenv("NOTIFIER_LOG_LEVEL"))
    sleep_duration = int(getenv("NOTIFIER_SLEEP_DURATION"))
    asyncio.run(notify(database_connection(), sleep_duration))


if __name__ == "__main__":  # pragma: no cover
    start_notifications()
