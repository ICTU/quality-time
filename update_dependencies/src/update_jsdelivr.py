"""Updater script for jsdelivr CDN URLs (limited to NPM packages in the Sphinx config at the moment)."""

import sys
from pathlib import Path

import requests
from packaging.version import InvalidVersion, Version

from filesystem import update_file
from log import get_logger

LOG = get_logger("jsdelivr")
JSDELIVR_URL_RE = r"https://cdn.jsdelivr.net/npm/(?P<dependency>[\w-]+)@(?P<version>[\d\.]+)"


def get_latest_version(dependency: str, current_version_string: str) -> str:
    """Fetch the latest version for the dependency."""
    url = f"https://data.jsdelivr.com/v1/packages/npm/{dependency}"
    current_version = Version(current_version_string)
    headers = {"User-Agent": "Dependency update script for Quality-time (https://github.com/ictu/quality-time)"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    json = response.json()
    latest_tag = json.get("tags", {}).get("latest", "")
    try:
        latest_version = Version(latest_tag)
    except InvalidVersion:
        LOG.invalid_version(f"{dependency}", f"'{latest_tag}'")
        latest_version = Version("0.0.0")
    return str(max(latest_version, current_version))


if __name__ == "__main__":  # pragma: no cover
    sphinx_config_py = Path.cwd() / "docs" / "src" / "conf.py"
    sys.exit(update_file(sphinx_config_py, JSDELIVR_URL_RE, get_latest_version, LOG))
