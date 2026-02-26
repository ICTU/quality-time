"""File manipulation methods."""

import re
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

    from log import Logger


def glob(glob_pattern: str, start: Path | None = None) -> Iterator[Path]:
    """Return an iterator over all paths matching the given glob pattern."""
    if start is None:
        start = Path.cwd()
    path_parts_to_ignore = {"build", "node_modules", "__pycache__"}
    for path in start.rglob(glob_pattern):
        relative_path = path.relative_to(start)
        if any(part.startswith(".") for part in relative_path.parts):
            continue
        if any(part in path_parts_to_ignore for part in relative_path.parts):
            continue
        yield path


def _update_line(line: str, regexp: str, get_new_version: Callable[[str, str], str], logger: Logger) -> str:
    """Update the line with the new version if any or return the line unchanged."""
    if match := re.search(regexp, line):
        dependency = match.group("dependency")
        version = match.group("version")
        latest_version = get_new_version(dependency, version)
        if latest_version > version:
            logger.new_version(dependency, latest_version)
            return line.replace(version, latest_version)
    return line


def update_file(path: Path, regexp: str, get_new_version: Callable[[str, str], str], logger: Logger) -> int:
    """Update the lines in the file and write back the file if the new lines are different from the old lines."""
    logger.path(path)
    old_lines = path.read_text().splitlines()
    new_lines = [_update_line(line, regexp, get_new_version, logger) for line in old_lines]
    if old_lines != new_lines:
        path.write_text("\n".join(new_lines) + "\n")
    return 0


def update_files(
    glob_pattern: str,
    regexp: str,
    get_new_version: Callable[[str, str], str],
    logger: Logger,
    start: Path | None = None,
) -> int:
    """Update the files using the regexp to find the current version and get_new_version to find new versions."""
    results = {update_file(path, regexp, get_new_version, logger) for path in glob(glob_pattern, start)}
    return max(results, default=0)
