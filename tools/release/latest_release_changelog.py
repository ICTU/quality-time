#!/usr/bin/env python
"""Extract the changes for the latest release from the changelog markdown file."""

import sys
from pathlib import Path


def latest_release(file_path: Path) -> str:
    """Extract changes for the latest release."""
    with file_path.open(encoding="utf-8") as file:
        lines = file.readlines()

    extracted_lines: list[str] = []

    for line in lines:
        if line.startswith("## v"):  # Found a header of a release
            if extracted_lines:  # It's the header of the second release, we're done
                break
            extracted_lines.append(line)  # It's the first release, add the header
        elif extracted_lines:  # We're between the header of the first and the second release
            extracted_lines.append(line)

    # Remove one # so the release header is level 1
    return "".join(line.removeprefix("#") for line in extracted_lines)


if __name__ == "__main__":
    sys.stdout.write(latest_release(Path(sys.argv[1])))
