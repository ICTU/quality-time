"""Package.json updater script finds package.json files and updates dependencies to latest versions."""

import json
import subprocess  # nosec
import sys
from typing import TYPE_CHECKING

from filesystem import glob
from log import logger

if TYPE_CHECKING:
    from pathlib import Path

LOG = logger("package.json")


def update_package_json(package_json: Path) -> None:
    """Update the package.json and package-lock.json."""
    LOG.path(package_json)
    subprocess_kwargs = {"cwd": package_json.parent, "capture_output": True, "text": True, "check": True}
    npm_outdated = ["npm", "outdated", "--silent", "--json"]
    try:
        outdated = subprocess.run(npm_outdated, **subprocess_kwargs).stdout  # type: ignore[call-overload] # noqa: PLW1510, S603 # nosec
    except subprocess.CalledProcessError as error:
        outdated = error.stdout
    for package, version in json.loads(outdated).items():
        LOG.new_version(package, version["latest"])
    npm_update = ["npm", "update", "--fund=false", "--ignore-scripts", "--silent"]
    subprocess.run(npm_update, **subprocess_kwargs)  # type: ignore[call-overload] # noqa: PLW1510, S603 # nosec


def update_package_jsons() -> int:
    """Find all package.json files, update them, and then update the package-lock.json files."""
    for package_json in glob("package.json"):
        update_package_json(package_json)
    return 0


if __name__ == "__main__":
    sys.exit(update_package_jsons())
