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
    version_tags = [tag for tag in repo.tags if re.match(version_re, tag.tag.tag.strip("v"), re.MULTILINE)]
    latest_tag = sorted(version_tags, key=lambda tag: tag.commit.committed_datetime)[-1]
    return latest_tag.tag.tag.strip("v")


def parse_arguments() -> tuple[str, bool]:
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
  - the changelog contains no release candidates"""
    parser = ArgumentParser(description=description, epilog=epilog, formatter_class=RawDescriptionHelpFormatter)
    allowed_bumps_in_rc_mode = ["rc", "rc-major", "rc-minor", "rc-patch", "drop-rc"]  # rc = release candidate
    allowed_bumps = ["rc-patch", "rc-minor", "rc-major", "patch", "minor", "major"]
    bumps = allowed_bumps_in_rc_mode if "rc" in current_version else allowed_bumps
    parser.add_argument("bump", choices=bumps)
    parser.add_argument(
        "-c", "--check-preconditions-only", action="store_true", help="only check the preconditions and then exit"
    )
    arguments = parser.parse_args()
    return arguments.bump, arguments.check_preconditions_only


def check_preconditions(bump: str) -> None:
    """Check preconditions for version bump."""
    messages = []
    release_folder = get_release_folder()
    if pathlib.Path.cwd() != release_folder:
        messages.append(f"The current folder is not the release folder. Please change directory to {release_folder}.")
    root = release_folder.parent
    messages.extend(failed_preconditions_repo(root))
    messages.extend(failed_preconditions_changelog(bump, root))
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


def main() -> None:
    """Create the release."""
    os.environ["RELEASE_DATE"] = datetime.date.today().isoformat()  # Used by bump-my-version to update CHANGELOG.md
    bump, check_preconditions_only = parse_arguments()
    check_preconditions(bump)
    if check_preconditions_only:
       return
    # See https://github.com/callowayproject/bump-my-version?tab=readme-ov-file#add-support-for-pre-release-versions
    # for how bump-my-version deals with pre-release versions
    if bump.startswith("rc-"):
        bump = bump.split("-", maxsplit=1)[1]  # Create a patch, minor, or major release candidate
    elif bump == "drop-rc":
        bump = "pre_release_label"  # Bump the pre-release label from "rc" to "final" (which is optional and omitted)
    elif bump == "rc":
        bump = "pre_release_number"  # Bump the release candidate number
    subprocess.run(("bump-my-version", "bump", bump), check=True)
    subprocess.run(("git", "push", "--follow-tags"), check=True)


if __name__ == "__main__":
    main()
