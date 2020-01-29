#!/usr/bin/env python

"""Release the application."""

import datetime
import argparse
import os
import subprocess
import sys

import git


def parse_arguments():
    """Return the command line arguments."""
    output = subprocess.check_output(("bump2version", "--list", "--dry-run", "--allow-dirty", "part"), text=True)
    current_version = [line for line in output.split("\n") if line.startswith("current_version")][0].split("=")[1]
    parser = argparse.ArgumentParser(description=f"Release Quality-time. Current version is {current_version}.")
    rc_choices = ("rc",) if "rc" in current_version else ("rc-patch", "rc-minor", "rc-major")
    parser.add_argument("bump", choices=rc_choices + ("patch", "minor", "major"))
    return current_version, parser.parse_args().bump


def main():
    """Create the release."""
    if git.Repo(".").active_branch.name != "master":
        sys.exit("Please release Quality-time from the master branch.")
    os.environ["RELEASE_DATE"] = datetime.date.today().isoformat()  # Used by bump2version to update CHANGELOG.md
    current_version, bump = parse_arguments()
    if bump.startswith("rc-"):
        bump, pre_bump = bump.split("-")
        subprocess.run(("bump2version", "--allow-dirty", pre_bump), check=True)
    subprocess.run(("bump2version", "--allow-dirty", bump), check=True)
    subprocess.run(("git", "push", "--follow-tags"), check=True)


if __name__ == "__main__":
    main()
