"""Dependency update cooldown helpers."""

import tomllib
from datetime import UTC, datetime, timedelta
from pathlib import Path


def _read_cooldown_days() -> int:
    """Read the cooldown period (in days) from this tool's pyproject.toml [tool.uv] exclude-newer."""
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    with pyproject.open("rb") as pyproject_file:
        exclude_newer = tomllib.load(pyproject_file)["tool"]["uv"]["exclude-newer"]
    return int(exclude_newer.split()[0])  # The exclude-newer value is "<number> days"


COOLDOWN_DAYS = _read_cooldown_days()


def within_cooldown(timestamp: datetime | None) -> bool:
    """Return whether the timestamp falls within the cooldown period."""
    if timestamp is None:
        return False
    return datetime.now(UTC) - timestamp < timedelta(days=COOLDOWN_DAYS)
