"""GitHub Action updater script finds GitHub workflows and updates 'uses' keys to latest versions.

If an environment variable GITHUB_TOKEN is set, the script will use it to increase the GitHub rate limit.
"""

import os
import sys
from functools import cache
from pathlib import Path

import requests
from packaging.version import InvalidVersion, Version

from filesystem import update_files
from log import get_logger

LOG = get_logger("github action")
ACTION_RE = r"uses: (?P<dependency>[\w\d\./-]+)@v?(?P<version>[\d\w\.\-]+)"


@cache
def get_latest_version(action: str, current_version_string: str) -> str:
    """Fetch the latest version for the action."""
    organization, repository, *_path = action.split("/")
    current_version = Version(current_version_string)
    url = f"https://api.github.com/repos/{organization}/{repository}/releases/latest"
    headers = {"Authorization": f"Bearer {github_token}"} if (github_token := os.environ.get("GITHUB_TOKEN")) else {}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    json = response.json()
    try:
        latest_version = Version(json.get("tag_name", "").strip("v"))
    except InvalidVersion:
        LOG.invalid_version(f"{organization}/{repository}", f"'{json.get('tag_name', '')}'")
        latest_version = Version("0.0.0")
    return str(max(latest_version, current_version))


if __name__ == "__main__":  # pragma: no cover
    sys.exit(update_files("*.yml", ACTION_RE, get_latest_version, LOG, start=Path.cwd() / ".github" / "workflows"))
