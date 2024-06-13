"""Determine the Python requirements files.

The script returns the requirements files as space separated string:

$ requirements_files.py
requirements/requirements.txt requirements/requirements-dev.txt

The script takes an optional template argument that is used to wrap each requirements filename. For example:

$ requirements_files.py "-r %s"
-r requirements/requirements.txt -r requirements/requirements-dev.txt
"""

import sys
from pathlib import Path


def requirements_files() -> list[str]:
    """Return the Python requirements files in the requirements directory."""
    requirements_files = Path(".").glob("requirements/requirements*.txt")
    # We never return the internal requirements file, because it does not need to be checked nor compiled
    return [str(filename) for filename in requirements_files if "requirements-internal" not in filename.name]


if __name__ == "__main__":
    template = sys.argv[1] if len(sys.argv) > 1 else "%s"
    print(" ".join([template % filename for filename in requirements_files()]))
