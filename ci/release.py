#!/usr/bin/env python

"""Release the application."""

import datetime
import argparse
import os
import subprocess
import sys

import git


def get_current_version() -> str:
    """Return the current version."""
    output = subprocess.check_output(("bump2version", "--list", "--dry-run", "--allow-dirty", "part"), text=True)
    return [line for line in output.split("\n") if line.startswith("current_version")][0].split("=")[1]


def get_next_version(current_version: str, bump: str) -> str:
    """Return the next version."""
    output = subprocess.check_output(("bump2version", "--list", "--dry-run", "--allow-dirty", "--current-version", current_version, bump), text=True)
    return [line for line in output.split("\n") if line.startswith("new_version")][0].split("=")[1]


def parse_arguments():
    """Return the command line arguments."""
    current_version = get_current_version()
    parser = argparse.ArgumentParser(description=f"Release Quality-time. Current version is {current_version}.")
    rc_choices = ("rc",) if "rc" in current_version else ("rc-patch", "rc-minor", "rc-major")
    parser.add_argument("bump", choices=rc_choices + ("patch", "minor", "major"))
    return current_version, parser.parse_args().bump


def main():
    """Create the release."""
    #if git.Repo(".").active_branch.name != "master":
    #    sys.exit("Please release Quality-time from the master branch.")
    os.environ["RELEASE_DATE"] = datetime.date.today().isoformat()  # Used by bump2version to update CHANGELOG.md
    current_version, bump = parse_arguments()
    if bump.startswith("rc-"):
        bump, pre_bump = bump.split("-")
        intermediate_version = get_next_version(current_version, pre_bump)
        new_version = get_next_version(intermediate_version, bump)
        print(current_version, intermediate_version, new_version)
        subprocess.run(("bump2version", "--new-version", new_version, "--allow-dirty", "--no-commit", "--no-tag", bump), check=True)
    else:
        subprocess.run(("bump2version", "--allow-dirty", "--no-commit", "--no-tag", bump), check=True)
    #subprocess.run(("git", "push", "--follow-tags"), check=True)


if __name__ == "__main__":
    main()
