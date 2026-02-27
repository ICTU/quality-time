"""Work-around for the missing `uv update` command, see https://github.com/astral-sh/uv/issues/6794.

Note: This script only considers matching versions ("==") for upgrading. Version specs with other version clauses
("<=", "~=", etc.) are ignored. This means that a version can be prevented from being updated, by using
"package<=max version" as version spec.
"""

import re
import sys
from typing import TYPE_CHECKING

from filesystem import glob
from log import get_logger
from process import run

if TYPE_CHECKING:
    from pathlib import Path

LOG = get_logger("pyproject.toml")


class Versions:
    """Mapping of package names to versions."""

    def __init__(self, versions: dict[str, str]) -> None:
        """Keep track of the versions, a mapping of package names to latest versions."""
        self.versions = versions

    def get_package_spec(self, match: re.Match) -> str:
        """Return a package spec for the package name with the latest version if available or the old version if not."""
        name = match.group("name")
        version = self.versions.get(name.lower(), match.group("version"))
        return f'"{name}=={version}"'


def update_pyproject_toml(pyproject_toml: Path) -> None:
    """Update the pyproject.toml file with latest version of dependencies."""
    LOG.path(pyproject_toml)
    uv_tree = [
        "uv",
        "tree",
        "--directory",
        str(pyproject_toml.parent),
        "--frozen",
        "--quiet",
        "--depth=1",
        "--all-groups",
        "--outdated",
    ]
    outdated = run(uv_tree)
    lines_with_updates = [line for line in outdated.splitlines() if " (latest: " in line]
    for line in lines_with_updates:
        LOG.new_version(line.split()[1], line.split()[-1].lstrip("v").rstrip(")"))
    latest_versions = Versions(
        {line.split()[1]: line.split()[-1].lstrip("v").rstrip(")") for line in lines_with_updates}
    )
    package_spec = re.compile(r'"(?P<name>[A-Za-z0-9_.\-]+)==(?P<version>[A-Za-z0-9_.\-]+)"')
    current_pyproject_toml = pyproject_toml.read_text()
    updated_pyproject_toml = package_spec.sub(latest_versions.get_package_spec, current_pyproject_toml)
    if updated_pyproject_toml != current_pyproject_toml:
        pyproject_toml.write_text(updated_pyproject_toml)


def update_uv_lock(pyproject_toml: Path) -> None:
    """Update the uv.lock file for the pyproject.toml."""
    LOG.path(pyproject_toml.parent / "uv.lock")
    run(["uv", "sync", "--directory", str(pyproject_toml.parent), "--upgrade", "--quiet", "--no-progress"])


def update_pyproject_tomls() -> int:
    """Find all pyproject.toml files, update them, and then update the uv.lock files."""
    files = list(glob("pyproject.toml"))
    for pyproject_toml in files:
        update_pyproject_toml(pyproject_toml)
    for pyproject_toml in files:
        update_uv_lock(pyproject_toml)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(update_pyproject_tomls())
