#!/usr/bin/env python

"""Release the application."""

import datetime
import os
import pathlib
import re
import subprocess
import sys
import tomllib
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from typing import cast

import git


def get_release_folder() -> pathlib.Path:
    """Return the release folder."""
    return pathlib.Path(__file__).resolve().parent


def get_version() -> str:
    """Return the current version."""
    release_folder = get_release_folder()
    repo = git.Repo(release_folder.parent)
    with pathlib.Path(release_folder / "pyproject.toml").open(mode="rb") as py_project_toml_fp:
        py_project_toml = tomllib.load(py_project_toml_fp)
    version_re = py_project_toml["tool"]["bumpversion"]["parse"]
    version_tags = [tag for tag in repo.tags if tag.tag and re.match(version_re, tag.tag.tag.strip("v"), re.MULTILINE)]
    latest_tag = sorted(version_tags, key=lambda tag: tag.commit.committed_datetime)[-1]
    # We cast latest_tag.tag to TagObject because we know it cannot be None, given how version_tags is constructed
    return cast(git.TagObject, latest_tag.tag).tag.strip("v")


def parse_arguments() -> tuple[str, str, bool]:
    """Return the command line arguments."""
    current_version = get_version()
    description = f"Release Quality-time. Current version is {current_version}."
    epilog = """preconditions for release:
  - the current folder is the release folder
  - the current branch is master
  - the local HEAD of master is equal to the remote HEAD of master
  - the workspace has no uncommitted changes
  - the workspace has no untracked files
  - the changelog has an '[Unreleased]' header
  - the changelog contains no release candidates
  - the new release has been added to the version overview"""
    parser = ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=RawDescriptionHelpFormatter,
    )
    allowed_bumps_in_rc_mode = [
        "rc",
        "rc-major",
        "rc-minor",
        "rc-patch",
        "drop-rc",
    ]  # rc = release candidate
    allowed_bumps = ["rc-patch", "rc-minor", "rc-major", "patch", "minor", "major"]
    bumps = allowed_bumps_in_rc_mode if "rc" in current_version else allowed_bumps
    parser.add_argument("bump", choices=bumps)
    parser.add_argument(
        "-c",
        "--check-preconditions-only",
        action="store_true",
        help="only check the preconditions and then exit",
    )
    arguments = parser.parse_args()
    return arguments.bump, current_version, arguments.check_preconditions_only


def check_preconditions(bump: str, current_version: str, rc: bool = False) -> None:
    """Check preconditions for version bump."""
    messages = []
    release_folder = get_release_folder()
    if pathlib.Path.cwd() != release_folder:
        messages.append(f"The current folder is not the release folder. Please change directory to {release_folder}.")
    root = release_folder.parent
    messages.extend(failed_preconditions_repo(root))
    messages.extend(failed_preconditions_changelog(bump, root))
    if not rc:
        messages.extend(failed_preconditions_version_overview(current_version, root))
    if messages:
        formatted_messages = "\n".join([f"- {message}" for message in messages])
        sys.exit(f"Please fix these issues before releasing Quality-time:\n{formatted_messages}\n")


def failed_preconditions_repo(root: pathlib.Path) -> list[str]:
    """Check that the repo is in pristine condition."""
    messages = []
    repo = git.Repo(root)
    origin = git.Remote(repo, "origin")
    origin.fetch()
    if repo.active_branch.name != "master":
        messages.append("The current branch is not the master branch.")
    if repo.heads.master.commit != repo.remotes.origin.refs.master.commit:
        messages.append(
            f"The local HEAD of master ({repo.heads.master.commit}) is not equal to the remote HEAD of "
            f"master ({repo.remotes.origin.refs.master.commit})."
        )
    if repo.is_dirty():
        messages.append("The workspace has uncommitted changes.")
    if repo.untracked_files:
        messages.append("The workspace has untracked files.")
    return messages


def failed_preconditions_changelog(bump: str, root: pathlib.Path) -> list[str]:
    """Check that the changelog is properly prepared."""
    messages = []
    changelog = root / "docs" / "src" / "changelog.md"
    with changelog.open() as changelog_file:
        changelog_text = changelog_file.read()
    if "[Unreleased]" not in changelog_text:
        messages.append(f"The changelog ({changelog}) has no '[Unreleased]' header.")
    if bump == "drop-rc" and "-rc." in changelog_text:
        messages.append(
            f"The changelog ({changelog}) still contains release candidates; remove "
            "the release candidates and move their changes under the '[Unreleased]' header."
        )
    return messages


def failed_preconditions_version_overview(current_version: str, root: pathlib.Path) -> list[str]:
    """Check that the version overview is properly prepared."""
    version_overview = root / "docs" / "src" / "versioning.md"
    with version_overview.open() as version_overview_file:
        version_overview_lines = version_overview_file.readlines()
    missing = f"The version overview ({version_overview}) does not contain"
    previous_line = ""
    for line in version_overview_lines:
        if line.startswith(f"| v{current_version} "):
            if previous_line.startswith("| v"):
                today = utc_today().isoformat()
                release_date = previous_line.split(" | ")[1].strip()
                if release_date != today:  # Second column is the release date column
                    return [f"{missing} the release date. Expected today: '{today}', found: '{release_date}'."]
                return []  # All good: current version, next version, and release date found
            return [f"{missing}) the new version."]
        previous_line = line
    return [f"{missing} the current version ({current_version})."]


def utc_today() -> datetime.date:
    """Return today in UTC."""
    return datetime.datetime.now(tz=datetime.UTC).date()


def main() -> None:
    """Create the release."""
    os.environ["RELEASE_DATE"] = utc_today().isoformat()  # Used by bump-my-version to update CHANGELOG.md
    bump, current_version, check_preconditions_only = parse_arguments()
    # See https://github.com/callowayproject/bump-my-version?tab=readme-ov-file#add-support-for-pre-release-versions
    # for how bump-my-version deals with pre-release versions
    create_rc = bump.startswith("rc")  # needs to be True for case "rc", and "rc-*"
    if bump.startswith("rc-"):
        bump = bump.split("-", maxsplit=1)[1]  # Create a patch, minor, or major release candidate
    check_preconditions(bump, current_version, create_rc)
    if check_preconditions_only:
        return
    cmd = ["bump-my-version", "bump"]
    if bump == "drop-rc":
        cmd.append("pre_release_label")  # Bump the pre-release label from "rc" to "final" (being optional and omitted)
    elif bump == "rc":
        cmd.append("pre_release_number")  # Bump the release candidate number, when already on a -rc version
    else:
        cmd.append(bump)
    subprocess.run(cmd, check=True)  # noqa: S603
    if create_rc:
        changelog_path = get_release_folder().parent / "docs" / "src" / "changelog.md"
        subprocess.run(("git", "checkout", "HEAD~1", "--", changelog_path), check=True)
        subprocess.run(("git", "add", changelog_path), check=True)
        subprocess.run(("git", "commit", "-m", "Reset changelog after producing release candidate"), check=True)
    subprocess.run(("git", "push", "--follow-tags"), check=True)  # noqa: S603


if __name__ == "__main__":
    main()
