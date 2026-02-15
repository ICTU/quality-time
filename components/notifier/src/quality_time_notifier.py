"""Notifier."""

import asyncio
import logging
import os
from typing import NoReturn

from rich.logging import RichHandler

from shared.initialization.database import get_database, mongo_client

from notifier.notifier import notify


def start_notifications() -> NoReturn:
    """Notify indefinitely."""
    logging.basicConfig(datefmt="%Y-%m-%d %H:%M:%S", format="%(message)s", handlers=[RichHandler()])
    logging.getLogger().setLevel(str(os.getenv("NOTIFIER_LOG_LEVEL", "WARNING")))
    sleep_duration = int(os.getenv("NOTIFIER_SLEEP_DURATION", "60"))
    with mongo_client() as client:
        asyncio.run(notify(get_database(client), sleep_duration))


if __name__ == "__main__":  # pragma: no cover
    start_notifications()
