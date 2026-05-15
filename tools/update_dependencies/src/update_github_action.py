"""GitHub Action updater script finds GitHub workflows and updates 'uses' keys to latest versions.

If an environment variable GITHUB_TOKEN is set, the script will use it to increase the GitHub rate limit.
"""

import sys
from functools import cache
from pathlib import Path

from packaging.version import Version

from filesystem import update_files
from github import get_latest_release_json
from log import get_logger
from version import DependencyVersion

LOG = get_logger("github action")
ACTION_RE = r"uses: (?P<dependency>[\w\d\./-]+)@(?P<commit_sha>[a-f0-9]{40}) # v?(?P<version>[\d\w\.\-]+)"


@cache
def get_latest_version(action: str, current_version_string: str) -> DependencyVersion:
    """Fetch the latest version for the action."""
    owner, repository, *_path = action.split("/")
    current_version = Version(current_version_string)
    json = get_latest_release_json(owner, repository)
    if "tag_name" in json:
        latest_tag = json["tag_name"].strip("v")
        latest_version = Version(latest_tag)
    else:
        LOG.no_version(f"{owner}/{repository}")
        latest_version = Version("0.0.0")
    changes = json.get("body", "")
    return DependencyVersion(str(max(latest_version, current_version)), changes, json.get("commit_sha", ""))


if __name__ == "__main__":  # pragma: no cover
    sys.exit(update_files("*.yml", ACTION_RE, get_latest_version, LOG, start=Path.cwd() / ".github" / "workflows"))
