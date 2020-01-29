#!/usr/bin/env python

"""Release the application."""

import datetime
import argparse
import os
import subprocess
import sys
from typing import Tuple

import git


def get_version(current_version: str = None, bump: str = "whatever") -> str:
    """Return the current version or the next version relative to the specified current version."""
    current_version_args = f"--current-version {current_version} " if current_version else "" 
    command = f"bump2version --list --dry-run --allow-dirty {current_version_args}{bump}"
    output = subprocess.check_output(command.split(" "), text=True)
    version_type = f"{'new' if current_version else 'current'}_version"
    return [line for line in output.split("\n") if line.startswith(version_type)][0].split("=")[1]


def parse_arguments() -> Tuple[str, str]:
    """Return the command line arguments."""
    current_version = get_version()
    parser = argparse.ArgumentParser(description=f"Release Quality-time. Current version is {current_version}.")
    choices = ("rc", "drop-rc") if "rc" in current_version else ("rc-patch", "rc-minor", "rc-major", "patch", "minor", "major")
    parser.add_argument("bump", choices=choices)
    return current_version, parser.parse_args().bump


def main():
    """Create the release."""
    if git.Repo(".").active_branch.name != "master":
        sys.exit("Please release Quality-time from the master branch.")
    os.environ["RELEASE_DATE"] = datetime.date.today().isoformat()  # Used by bump2version to update CHANGELOG.md
    current_version, bump = parse_arguments()
    if bump.startswith("rc-"):
        rc_bump, non_rc_bump = bump.split("-")
        # Determine the new version by first bumping the patch/minor/major part and then bumping/adding the rc part
        new_version = get_version(get_version(current_version, non_rc_bump), rc_bump)
        command = f"bump2version --new-version {new_version} whatever"
    elif bump == "drop-rc":
        new_version = current_version.split("-")[0]
        command = f"bump2version --new-version {new_version} whatever"
    else:
        command = f"bump2version {bump}"
    subprocess.run(command.split(" "), check=True)
    subprocess.run(("git", "push", "--follow-tags"), check=True)


if __name__ == "__main__":
    main()
