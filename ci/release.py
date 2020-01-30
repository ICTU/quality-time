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


def get_version() -> str:
    """Return the current version."""
    command = f"bump2version --list --dry-run --allow-dirty part-is-a-mandatory-argument" 
    output = subprocess.check_output(command.split(" "), text=True)
    return [line for line in output.split("\n") if line.startswith("current_version")][0].split("=")[1]


def parse_arguments() -> Tuple[str, str]:
    """Return the command line arguments."""
    current_version = get_version()
    parser = argparse.ArgumentParser(description=f"Release Quality-time. Current version is {current_version}.")
    choices = ("rc", "drop-rc") if "rc" in current_version else ("rc-patch", "rc-minor", "rc-major", "patch", "minor", "major")
    parser.add_argument("bump", choices=choices)
    return current_version, parser.parse_args().bump


def main():
    """Create the release."""
    #if git.Repo(".").active_branch.name != "master":
    #    sys.exit("Please release Quality-time from the master branch.")
    with pathlib.Path("docs/CHANGELOG.md").open() as changelog:
        if "[Unreleased]" not in changelog.read():
            sys.exit("Please add an [Unreleased] header to docs/CHANGELOG.md.")

    os.environ["RELEASE_DATE"] = datetime.date.today().isoformat()  # Used by bump2version to update CHANGELOG.md
    current_version, bump = parse_arguments()
    commands = []
    if bump.startswith("rc-"):
        rc_bump, non_rc_bump = bump.split("-")
        commands.append(["bump2version", "--no-tag", "--no-commit", "--allow-dirty", non_rc_bump])  # FIXME: Remove allow dirty
        message = f'"Bump version: {current_version} → {{new_version}}"'
        commands.append(["bump2version", "--config-file", ".bumpversion-rc.cfg", "--message", message, "--tag-message", message, "--allow-dirty", "--no-commit", "--no-tag", rc_bump])  # Previous command dirties the work space so allow dirty
    elif bump == "drop-rc":
        new_version = current_version.split("-")[0]
        commands.append(["bump2version", "--new-version", new_version, "whatever"])
    else:
        commands.append(["bump2version", bump])
    for command in commands:
        command.extend(["--no-commit", "--no-tag", "--allow-dirty"])  # FIXME: to be removed
        subprocess.run(tuple(command), check=True)
    #subprocess.run(("git", "push", "--follow-tags"), check=True)


if __name__ == "__main__":
    main()
