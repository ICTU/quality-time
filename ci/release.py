#!/usr/bin/env python

"""Release the application."""

import os
import re
import sys


def check_version_number(version: str) -> None:
    """Check that the release version number conforms to http://semver.org/spec/v2.0.0.html."""
    if version.count(".") != 2:
        sys.exit("Version number should have two dots.")
    for index, part in enumerate(version.split(".")):
        if not re.match(r"^\d+$", part):
            sys.exit(f"Part {index+1} of {version} is not a positive number.")
    for index, part in enumerate(version.split(".")):
        if re.match(r"^0\d+$", part):
            sys.exit(f"Part {index+1} of {version} has leading zeroes.")

def main():
    """Create the release."""
    release = sys.argv[1]
    check_version_number(release)
    os.system(f"cd components/frontend && npm version --no-git-tag-version --allow-same-version {release}")
    os.system(f"git tag v{release} && git push --tags")

if __name__ == "__main__":
    main()
