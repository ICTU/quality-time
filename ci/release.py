#!/usr/bin/env python

"""Release the application."""

import argparse
import datetime
import os
import pathlib
import subprocess
import sys
from typing import Tuple

import git

PART = "part-is-a-mandatory-bump2version-argument-even-when-not-used"


def get_version() -> str:
    """Return the current version."""
    command = f"bump2version --list --dry-run --allow-dirty {PART}"
    output = subprocess.check_output(command.split(" "), text=True)
    return [line for line in output.split("\n") if line.startswith("current_version")][0].split("=")[1]


def parse_arguments() -> Tuple[str, str]:
    """Return the command line arguments."""
    current_version = get_version()
    parser = argparse.ArgumentParser(description=f"Release Quality-time. Current version is {current_version}.")
    allowed_bumps_in_rc_mode = ("rc", "drop-rc")  # rc = release candidate
    allowed_bumps = ("rc-patch", "rc-minor", "rc-major", "patch", "minor", "major")
    bumps = allowed_bumps_in_rc_mode if "rc" in current_version else allowed_bumps
    parser.add_argument("bump", choices=bumps)
    return current_version, parser.parse_args().bump


def check_preconditions(bump: str):
    """Check preconditions for version bump."""
    messages = []
    repo = git.Repo(".")
    if repo.active_branch.name != "master":
        messages.append("The current branch is not the master branch.")
    if repo.is_dirty():
        messages.append("The workspace has uncommitted changes.")
    with pathlib.Path("docs/CHANGELOG.md").open() as changelog:
        changelog_text = changelog.read()
    if "[Unreleased]" not in changelog_text:
        messages.append("The change log (docs/CHANGELOG.md) has no '[Unreleased]' header.")
    if bump == "drop-rc" and "-rc." in changelog_text:
        messages.append(
            "The change log (docs/CHANGELOG.md) still contains release candidates; remove "
            "the release candidates and move their changes under the '[Unreleased]' header.")
    if messages:
        formatted_messages = "\n".join([f"- {message}" for message in messages])
        sys.exit(f"Please fix these issues before releasing Quality-time:\n{formatted_messages}\n")


def main():
    """Create the release."""
    os.environ["RELEASE_DATE"] = datetime.date.today().isoformat()  # Used by bump2version to update CHANGELOG.md
    current_version, bump = parse_arguments()
    check_preconditions(bump)
    commands = []
    if bump.startswith("rc-"):
        rc_bump, non_rc_bump = bump.split("-")
        commands.append(["bump2version", "--no-tag", "--no-commit", non_rc_bump])
        message = f"Bump version: {current_version} → {{new_version}}"
        # Previous command makes the work space dirty, so allow dirty in the next version bump
        commands.append(
            ["bump2version", "--config-file", ".bumpversion-rc.cfg", "--message", message, "--tag-message", message,
             "--allow-dirty", rc_bump])
    elif bump == "drop-rc":
        new_version = current_version.split("-")[0]
        commands.append(["bump2version", "--new-version", new_version, PART])
    else:
        commands.append(["bump2version", bump])
    for command in commands:
        subprocess.run(tuple(command), check=True)
    subprocess.run(("git", "push", "--follow-tags"), check=True)


if __name__ == "__main__":
    main()
