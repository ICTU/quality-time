"""Notifier."""

import asyncio
import logging
import os

from notifier.notifier import notify


if __name__ == "__main__":  # pragma: no cover
    logging.getLogger().setLevel(str(os.getenv("NOTIFIER_LOG_LEVEL", "WARNING")))
    internal_server_host = os.getenv("INTERNAL_SERVER_HOST", "localhost")
    internal_server_port = os.getenv("INTERNAL_SERVER_PORT", "5002")
    sleep_duration = int(os.getenv("NOTIFIER_SLEEP_DURATION", "60"))
    asyncio.run(notify(internal_server_host, internal_server_port, sleep_duration))
