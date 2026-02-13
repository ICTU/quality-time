# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "packaging>=26.0",
#     "requests>=2.32.5",
# ]
# ///

"""GitHub Action updater script finds GitHub workflows and updates 'uses' keys to latest versions.

If an environment variable GITHUB_TOKEN is set, the script will use it to increase the GitHub rate limit.
"""

import os
import re
import sys
from functools import cache
from pathlib import Path

import requests
from packaging.version import InvalidVersion, Version


@cache
def get_latest_version(organization: str, repository: str, current_version_string: str) -> str:
    """Fetch the latest version for the action."""
    current_version = Version(current_version_string)
    url = f"https://api.github.com/repos/{organization}/{repository}/releases/latest"
    headers = {"Authorization": f"Bearer {github_token}"} if (github_token := os.environ.get("GITHUB_TOKEN")) else {}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    json = response.json()
    try:
        latest_version = Version(json.get("tag_name", "").strip("v"))
    except InvalidVersion:
        sys.stderr.write(
            f"{sys.argv[0]}: got an invalid version for {organization}/{repository}: '{json.get('tag_name', '')}'\n"
        )
        latest_version = Version("0.0.0")
    return str(max(latest_version, current_version))


def update_workflow_yml_line(line: str) -> str:
    """Update the GitHub Action version if the line contains a uses statement, otherwise return the line unchanged."""
    if match := re.search(r"uses: (?P<action>[\w\d\./-]+)@v(?P<version>[\d\w\.\-]+)", line):
        action = match.group("action")
        version = match.group("version")
        organization, repository, *_path = action.split("/")
        return line.replace(version, get_latest_version(organization, repository, version))
    return line


def update_workflow_yml(workflow_yml: Path) -> None:
    """Update GitHub Action versions a workflow YAML file with latest version."""
    old_lines = workflow_yml.read_text().splitlines()
    new_lines = [update_workflow_yml_line(line) for line in old_lines]
    if old_lines != new_lines:
        workflow_yml.write_text("\n".join(new_lines) + "\n")


def update_workflow_ymls() -> int:
    """Find all workflow YAML files under the current working directory and update them."""
    for workflow_yml in (Path.cwd() / ".github" / "workflows").rglob("*.yml"):
        update_workflow_yml(workflow_yml)
    return 0


if __name__ == "__main__":
    sys.exit(update_workflow_ymls())
