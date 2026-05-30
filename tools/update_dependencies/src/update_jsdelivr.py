"""Updater script for jsdelivr CDN URLs (limited to NPM packages in the Sphinx config at the moment)."""

import re
import sys
from pathlib import Path

import requests
from packaging.version import InvalidVersion, Version

from log import get_logger
from npmjs import get_publication_datetime
from version import DependencyVersion

LOG = get_logger("jsdelivr")
HEADERS = {"User-Agent": "Dependency update script for Quality-time (https://github.com/ictu/quality-time)"}
# Match a jsDelivr npm URL together with the Subresource Integrity hash that follows it, so both stay in sync.
JSDELIVR_RE = re.compile(
    r"https://cdn\.jsdelivr\.net/npm/(?P<dependency>[\w-]+)@(?P<version>[\d.]+)"
    r".*?\"integrity\": \"(?P<sha>sha\d+-[A-Za-z0-9+/=]+)\"",
    re.DOTALL,
)


def get_latest_version(dependency: str, current_version_string: str) -> DependencyVersion:
    """Fetch the latest version and matching integrity hash for the dependency."""
    current_version = Version(current_version_string)
    latest_version = _get_latest_version(dependency, current_version)
    integrity = _get_integrity_hash(dependency, latest_version) if latest_version > current_version else ""
    published = get_publication_datetime(dependency, str(latest_version))
    return DependencyVersion(version=str(latest_version), sha=integrity, published=published)


def _get_latest_version(dependency: str, current_version: Version) -> Version:
    """Fetch the latest released version of the dependency from jsDelivr."""
    url = f"https://data.jsdelivr.com/v1/packages/npm/{dependency}"
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    latest_tag = response.json().get("tags", {}).get("latest", "")
    try:
        latest_version = Version(latest_tag)
    except InvalidVersion:
        LOG.invalid_version(dependency, f"'{latest_tag}'")
        latest_version = Version("0.0.0")
    return max(latest_version, current_version)


def _get_integrity_hash(dependency: str, version: Version) -> str:
    """Fetch the Subresource Integrity hash of the dependency's default file from jsDelivr."""
    url = f"https://data.jsdelivr.com/v1/packages/npm/{dependency}@{version}?structure=flat"
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    json = response.json()
    file_hash = next(file["hash"] for file in json["files"] if file["name"] == json["default"])
    return f"sha256-{file_hash}"


def update_jsdelivr(content: str) -> str:
    """Update the version and integrity hash of all jsDelivr URLs in the content."""

    def replace(match: re.Match[str]) -> str:
        dependency, version = match.group("dependency"), match.group("version")
        latest_version = get_latest_version(dependency, version)
        if latest_version.version == version:
            return match.group(0)
        LOG.new_version(dependency, latest_version)
        return match.group(0).replace(version, latest_version.version).replace(match.group("sha"), latest_version.sha)

    return JSDELIVR_RE.sub(replace, content)


if __name__ == "__main__":  # pragma: no cover
    sphinx_config_py = Path.cwd() / "docs" / "src" / "conf.py"
    LOG.path(sphinx_config_py)
    old_content = sphinx_config_py.read_text()
    new_content = update_jsdelivr(old_content)
    if new_content != old_content:
        sphinx_config_py.write_text(new_content)
    sys.exit(0)
