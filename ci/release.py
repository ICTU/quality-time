#!/usr/bin/env python

"""Release the application."""

import datetime
import argparse
import os
import subprocess


def parse_arguments():
    """Return the command line arguments."""
    bump = subprocess.check_output(("bump2version", "--list", "--dry-run", "--allow-dirty", "part"), text=True)
    current_version = [line for line in bump.split("\n") if line.startswith("current_version")][0].split("=")[1]
    parser = argparse.ArgumentParser(description=f'Release Quality-time. Current version is {current_version}.')
    parser.add_argument('version', choices=('patch', 'minor', 'major'))
    return parser.parse_args()


def main():
    """Create the release."""
    os.environ["RELEASE_DATE"] = datetime.date.today().isoformat()  # Used by bump2version to update CHANGELOG.md
    subprocess.run(("bump2version", parse_arguments().version), check=True)
    subprocess.run(("git", "push", "--follow-tags"), check=True)


if __name__ == "__main__":
    main()
