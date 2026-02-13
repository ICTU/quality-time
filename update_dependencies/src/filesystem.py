"""File system methods."""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator


def glob(pattern: str, start: Path | None = None) -> Iterator[Path]:
    """Return an iterator over all paths matching the given pattern."""
    if start is None:
        start = Path.cwd()
    path_parts_to_ignore = {"build", "node_modules", "__pycache__"}
    for path in start.rglob(pattern):
        if any(part.startswith(".") for part in path.parts):
            continue
        if any(part in path_parts_to_ignore for part in path.parts):
            continue
        yield path
