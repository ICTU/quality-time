#!/usr/bin/env python

"""Release the application."""

import subprocess
import sys


def main():
    """Create the release."""
    bump = sys.argv[1]
    assert bump in ('patch', 'minor', 'major')
    subprocess.run(("bumpversion", bump), check=True)
    subprocess.run(("git", "push", "--tags"), check=True)


if __name__ == "__main__":
    main()
