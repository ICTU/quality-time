"""Run processes."""

import subprocess  # nosec
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def run(command: list[str], cwd: Path | None = None) -> str:
    """Run the process."""
    try:
        return subprocess.run(command, capture_output=True, text=True, check=True, cwd=cwd).stdout  # noqa: S603 # nosec
    except subprocess.CalledProcessError as error:
        return error.stdout
