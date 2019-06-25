#!/usr/bin/env python

"""Release the application."""

import subprocess
import sys


def main():
    """Create the release."""
    bump = sys.argv[1]
    assert bump in ('patch', 'minor', 'major')
    output = subprocess.run(f"bumpversion --dry-run --list {bump}", capture_output=True, shell=True, text=True)
    new_version = [line for line in output.stdout.split("\n") if line.startswith("new_version")][0].split("=")[1]
    subprocess.run("bumpversion", bump)
    subprocess.run(f"git tag v{new_version} && git push --tags")


if __name__ == "__main__":
    main()
