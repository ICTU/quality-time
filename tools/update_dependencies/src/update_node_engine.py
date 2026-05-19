"""Node engine updater script updates the Node engine in package.json files to the Node base image version.

Note: this script does not update package-lock.json.
"""

import json
import re
import sys
from typing import TYPE_CHECKING

from filesystem import glob, update_file
from log import get_logger
from version import DependencyVersion

if TYPE_CHECKING:
    from pathlib import Path

LOG = get_logger("node engine")
NODE_IMAGE_RE = r"FROM node:(?P<version>[\d\.]+)"
NODE_ENGINE_RE = r'"(?P<dependency>node)": "(?P<version>[\d\.]+)"'


def has_node_engine(package_json: Path) -> bool:
    """Return whether the package.json file contains a Node engine."""
    package_json_contents = json.loads(package_json.read_text())
    return "engines" in package_json_contents and "node" in package_json_contents["engines"]


def node_base_image_version(dockerfile: Path) -> str:
    """Return the Node base image version, or empty string if the Dockerfile is missing or its base image isn't Node."""
    if not dockerfile.exists():
        return ""
    if match := next(re.match(NODE_IMAGE_RE, line) for line in dockerfile.read_text().splitlines()):
        return match.group("version")
    return ""


def find_node_dockerfile(package_json: Path) -> Path:
    """Find the Dockerfile to derive the Node engine from.

    Prefers the Dockerfile next to the package.json; for package.json files without a local Node-base Dockerfile
    (e.g. docs/), falls back to any other Dockerfile in the repo with a Node base image. If none is found, returns
    the local Dockerfile path (which doesn't exist or isn't Node-based) so the caller can use it to log the error.
    """
    local_dockerfile = package_json.parent / "Dockerfile"
    for dockerfile in [local_dockerfile, *glob("Dockerfile")]:
        if node_base_image_version(dockerfile):
            return dockerfile
    return local_dockerfile


def update_node_engine(package_json: Path) -> int:
    """Update the Node engine version based on the Docker base image."""
    dockerfile = find_node_dockerfile(package_json)
    if version := node_base_image_version(dockerfile):
        return update_file(package_json, NODE_ENGINE_RE, lambda *_args: DependencyVersion(version=version), LOG)
    LOG.expected_node_base_image(dockerfile)
    return 1


def update_node_engines() -> int:
    """Find all package.json files and update the Node engine."""
    results = {update_node_engine(pkg_json) for pkg_json in glob("package.json") if has_node_engine(pkg_json)}
    return max(results, default=0)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(update_node_engines())
