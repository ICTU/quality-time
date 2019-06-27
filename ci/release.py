#!/usr/bin/env python

"""Release the application."""

import argparse
import subprocess


def parse_arguments():
    """Return the command line arguments."""
    bump = subprocess.check_output(("bumpversion", "--list", "--dry-run", "--allow-dirty", "part"), text=True)
    current_version = [line for line in bump.split("\n") if line.startswith("current_version")][0].split("=")[1]
    parser = argparse.ArgumentParser(description=f'Release Quality-time. Current version is {current_version}.')
    parser.add_argument('version', choices=('patch', 'minor', 'major'))
    return parser.parse_args()


def main():
    """Create the release."""
    subprocess.run(("bumpversion", parse_arguments().version), check=True)
    subprocess.run(("git", "push", "--follow-tags"), check=True)


if __name__ == "__main__":
    main()
