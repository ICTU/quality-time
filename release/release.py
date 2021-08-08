#!/usr/bin/env python

"""Release the application."""

import datetime
import os
import pathlib
import subprocess  # skipcq: BAN-B404
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter

import git

PART = "part-is-a-mandatory-bump2version-argument-even-when-not-used"


def get_version() -> str:
    """Return the current version."""
    command = f"bump2version --list --dry-run --allow-dirty --no-configured-files {PART} .bumpversion.cfg"
    try:
        output = subprocess.check_output(command.split(" "), stderr=subprocess.STDOUT, text=True)  # skipcq: BAN-B603
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "<unknown>"
    return [line for line in output.split("\n") if line.startswith("current_version")][0].split("=")[1]


def parse_arguments() -> tuple[str, str, bool]:
    """Return the command line arguments."""
    current_version = get_version()
    description = f"Release Quality-time. Current version is {current_version}."
    epilog = """preconditions for release:
  - the current folder is the release folder
  - the current branch is master
  - the workspace has no uncommitted changes
  - the generated data model documentation is up-to-date
  - the change log has an '[Unreleased]' header
  - the change log contains no release candidates"""
    parser = ArgumentParser(description=description, epilog=epilog, formatter_class=RawDescriptionHelpFormatter)
    allowed_bumps_in_rc_mode = ["rc", "rc-major", "rc-minor", "rc-patch", "drop-rc"]  # rc = release candidate
    allowed_bumps = ["rc-patch", "rc-minor", "rc-major", "patch", "minor", "major"]
    bumps = allowed_bumps_in_rc_mode if "rc" in current_version else allowed_bumps
    parser.add_argument("bump", choices=bumps)
    parser.add_argument(
        "-c", "--check-preconditions-only", action="store_true", help="only check the preconditions and then exit"
    )
    arguments = parser.parse_args()
    return current_version, arguments.bump, arguments.check_preconditions_only


def check_preconditions(bump: str):
    """Check preconditions for version bump."""
    messages = []
    release_folder = pathlib.Path(__file__).resolve().parent
    if pathlib.Path.cwd() != release_folder:
        messages.append(f"The current folder is not the release folder. Please change directory to {release_folder}.")
    root = release_folder.parent
    repo = git.Repo(root)
    if repo.active_branch.name != "master":
        messages.append("The current branch is not the master branch.")
    if repo.is_dirty():
        messages.append("The workspace has uncommitted changes.")
    docs = root / "docs"
    create_metrics_and_sources = docs / "src" / "create_metrics_and_sources_md.py"
    subprocess.run(["python3", create_metrics_and_sources], check=True)  # skipcq: BAN-B603,BAN-B607
    metrics_and_sources = docs / "source" / "METRICS_AND_SOURCES.md"
    if repo.is_dirty(path=metrics_and_sources):
        messages.append(f"The generated data model documentation is out of date, please commit {metrics_and_sources}.")
    changelog = docs / "CHANGELOG.md"
    with changelog.open() as changelog_file:
        changelog_text = changelog_file.read()
    if "[Unreleased]" not in changelog_text:
        messages.append(f"The change log ({changelog}) has no '[Unreleased]' header.")
    if bump == "drop-rc" and "-rc." in changelog_text:
        messages.append(
            f"The change log ({changelog}) still contains release candidates; remove "
            "the release candidates and move their changes under the '[Unreleased]' header."
        )
    if messages:
        formatted_messages = "\n".join([f"- {message}" for message in messages])
        sys.exit(f"Please fix these issues before releasing Quality-time:\n{formatted_messages}\n")


def main() -> None:
    """Create the release."""
    os.environ["RELEASE_DATE"] = datetime.date.today().isoformat()  # Used by bump2version to update CHANGELOG.md
    current_version, bump, check_preconditions_only = parse_arguments()
    check_preconditions(bump)
    if check_preconditions_only:
        return
    commands = []
    if bump.startswith("rc-"):
        rc_bump, non_rc_bump = bump.split("-")
        commands.append(["bump2version", "--no-tag", "--no-commit", non_rc_bump])
        message = f"Bump version: {current_version} → {{new_version}}"
        # Previous command makes the work space dirty, so allow dirty in the next version bump
        commands.append(
            [
                "bump2version",
                "--config-file",
                ".bumpversion-rc.cfg",
                "--message",
                message,
                "--tag-message",
                message,
                "--allow-dirty",
                rc_bump,
            ]
        )
    elif bump == "drop-rc":
        new_version = current_version.split("-")[0]
        commands.append(["bump2version", "--new-version", new_version, PART])
    else:
        commands.append(["bump2version", bump])
    for command in commands:
        subprocess.run(tuple(command), check=True)  # skipcq: BAN-B603
    subprocess.run(("git", "push", "--follow-tags"), check=True)  # skipcq: BAN-B603


if __name__ == "__main__":
    main()
