"""Dependency update cooldown helpers."""

import os
from datetime import UTC, datetime, timedelta


def within_cooldown(timestamp: datetime | None) -> bool:
    """Return whether the timestamp falls within the configured cooldown period."""
    if timestamp is None:
        return False
    cooldown_days = int(os.environ.get("DEPENDENCY_UPDATE_COOLDOWN_DAYS", "0"))
    return datetime.now(UTC) - timestamp < timedelta(days=cooldown_days)
