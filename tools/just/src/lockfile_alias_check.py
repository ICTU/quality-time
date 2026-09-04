"""Fail on allowed package name aliases in the lockfile-lint config that the lock file does not use."""

import json
import sys
from pathlib import Path
from typing import Any


def lockfile_aliases(lockfile_json: dict[str, Any]) -> set[str]:
    """Return the package name aliases the lock file uses, in lockfile-lint's 'alias:package' notation."""
    aliases = set()
    for path, package in lockfile_json.get("packages", {}).items():
        if "node_modules/" not in path:
            continue  # The root package and the workspaces are not installed under an alias
        alias = path.rsplit("node_modules/", 1)[-1]
        if (name := package.get("name", alias)) != alias:  # Only aliased packages have a differing name
            aliases.add(f"{alias}:{name}")
    return aliases


def redundant_aliases(config_json: dict[str, Any], lockfile_json: dict[str, Any]) -> int:
    """Print the allowed package name aliases that the lock file does not use and return the exit code."""
    redundant = set(config_json.get("allowed-package-name-aliases", [])) - lockfile_aliases(lockfile_json)
    for alias in sorted(redundant):
        print(f"redundant allowed package name alias: {alias}")  # noqa: T201
    return 1 if redundant else 0


def read_json(path: Path) -> dict[str, Any]:
    """Read the JSON file, returning an empty dict if it does not exist."""
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def lockfile_path(config: dict[str, Any], folder: Path) -> Path:
    """Return the lock file that the config points to, refusing to leave the folder that contains the config."""
    path = (folder / config.get("path", "package-lock.json")).resolve()
    if not path.is_relative_to(folder.resolve()):
        sys.exit(f"the lock file path in the configuration points outside {folder}: {path}")
    return path


if __name__ == "__main__":  # pragma: no cover
    # Read the configuration from the folder the check runs in, as lockfile-lint itself does, so that no path needs to
    # be passed on the command line.
    config_file = Path(".lockfile-lintrc.json")
    lint_config = read_json(config_file)
    sys.exit(redundant_aliases(lint_config, read_json(lockfile_path(lint_config, config_file.parent))))
