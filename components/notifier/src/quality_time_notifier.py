"""Notifier."""

import asyncio

from notifier.notifier import notify


if __name__ == "__main__":
    asyncio.run(notify())  # pragma: no cover
