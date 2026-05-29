"""GitHub Action updater script finds GitHub workflows and updates 'uses' keys to latest versions.

If an environment variable GITHUB_TOKEN is set, the script will use it to increase the GitHub rate limit.
"""

import sys
from functools import cache
from pathlib import Path

from packaging.version import Version

from filesystem import update_files
from github import get_latest_release
from log import get_logger
from version import DependencyVersion

LOG = get_logger("github action")
ACTION_RE = r"uses: (?P<dependency>[\w\d\./-]+)@(?P<sha>[a-f0-9]{40}) # v?(?P<version>[\d\w\.\-]+)"


@cache
def get_latest_version(action: str, current_version_string: str) -> DependencyVersion:
    """Fetch the latest version for the action."""
    owner, repository, *_path = action.split("/")
    release = get_latest_release(owner, repository)
    if release is None:
        LOG.no_version(f"{owner}/{repository}")
        return DependencyVersion(current_version_string)
    if release.commit_sha is None:
        return DependencyVersion(current_version_string)
    latest_version = max(release.version, Version(current_version_string))
    return DependencyVersion(str(latest_version), release.body, release.commit_sha, published=release.published_at)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(update_files("*.yml", ACTION_RE, get_latest_version, LOG, start=Path.cwd() / ".github" / "workflows"))
