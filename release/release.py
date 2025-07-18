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
from typing import Any, cast

import git


def get_release_folder() -> pathlib.Path:
    """Return the release folder."""
    return pathlib.Path(__file__).resolve().parent


def read_pyproject_toml() -> dict[str, Any]:
    """Return the pyproject.toml file contents."""
    release_folder = get_release_folder()
    with pathlib.Path(release_folder / "pyproject.toml").open(mode="rb") as pyproject_toml_file:
        return tomllib.load(pyproject_toml_file)


def get_version() -> str:
    """Return the current version."""
    release_folder = get_release_folder()
    repo = git.Repo(release_folder.parent)
    pyproject_toml = read_pyproject_toml()
    version_re = pyproject_toml["tool"]["bumpversion"]["parse"]
    version_tags = [tag for tag in repo.tags if tag.tag and re.match(version_re, tag.tag.tag.strip("v"), re.MULTILINE)]
    latest_tag = sorted(version_tags, key=lambda tag: tag.commit.committed_datetime)[-1]
    # We cast latest_tag.tag to TagObject because we know it cannot be None, given how version_tags is constructed
    return cast(git.TagObject, latest_tag.tag).tag.strip("v")


def parse_arguments() -> tuple[str, str, bool, bool]:
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
    bumps = ["patch", "minor", "major"]
    if "rc" in current_version:
        bumps += ["rc", "release"]
    parser.add_argument("bump", choices=bumps)
    parser.add_argument(
        "-c",
        "--check-preconditions-only",
        action="store_true",
        help="only check the preconditions and then exit",
    )
    parser.add_argument(
        "--no-git-push",
        action="store_true",
        help="do not run git push as final step",
    )
    arguments = parser.parse_args()
    return arguments.bump, current_version, arguments.check_preconditions_only, arguments.no_git_push


def check_preconditions(bump: str, current_version: str) -> None:
    """Check preconditions for version bump."""
    messages = []
    release_folder = get_release_folder()
    if pathlib.Path.cwd() != release_folder:
        messages.append(f"The current folder is not the release folder. Please change directory to {release_folder}.")
    root = release_folder.parent
    messages.extend(failed_preconditions_repo(root))
    messages.extend(failed_preconditions_changelog(bump, root))
    if bump == "release":  # don't update the version overview for release candidates
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
    if bump == "release" and "-rc." in changelog_text:
        messages.append(
            f"The changelog ({changelog}) still contains release candidates; remove "
            "the release candidates and move their changes under the '[Unreleased]' header."
        )
    return messages


def failed_preconditions_version_overview(current_version: str, root: pathlib.Path) -> list[str]:
    """Check that the version overview contains the new version.

    Note: this check is only run when the version bump is 'release'.
    """
    version_overview = root / "docs" / "src" / "versioning.md"
    with version_overview.open() as version_overview_file:
        latest_version_line = next(line for line in version_overview_file if re.match(r"\| \*?\*?v\d+", line))
    columns = latest_version_line.split(" | ")
    latest_version = columns[0].strip("| v")
    release_date = columns[1].strip("| ")
    target_version = current_version.split("-rc.")[0]
    messages = []
    today = utc_today().isoformat()
    missing = f"The first line of the version overview table ({version_overview}) does not contain"
    if release_date != today:
        messages.append(f"{missing} the release date. Expected today: '{today}', found: '{release_date}'.")
    if latest_version != target_version:
        messages.append(f"{missing} the new version. Expected: '{target_version}', found: '{latest_version}'.")
    return messages


def utc_today() -> datetime.date:
    """Return today in UTC."""
    return datetime.datetime.now(tz=datetime.UTC).date()


def bump_my_version_spec() -> str:
    """Return the bump-my-version version to use."""
    pyproject_toml = read_pyproject_toml()
    tools = pyproject_toml["project"]["optional-dependencies"]["tools"]
    return next(spec for spec in tools if spec.split("==")[0] == "bump-my-version")


def main() -> None:
    """Create the release."""
    os.environ["RELEASE_DATE"] = utc_today().isoformat()  # Used by bump-my-version to update CHANGELOG.md
    bump, current_version, check_preconditions_only, no_git_push = parse_arguments()
    # See https://github.com/callowayproject/bump-my-version?tab=readme-ov-file#add-support-for-pre-release-versions
    # for how bump-my-version deals with pre-release versions
    check_preconditions(bump, current_version)
    if check_preconditions_only:
        return
    cmd = ["uvx", bump_my_version_spec(), "bump"]
    if bump == "release":
        cmd.append("pre_release_label")  # Bump the pre-release label from "rc" to "final" (being optional and omitted)
    elif bump == "rc":
        cmd.append("pre_release_number")  # Bump the release candidate number, when already on a -rc version
    else:
        cmd.append(bump)
    subprocess.run(cmd, check=True)  # noqa: S603
    for python_project_folder in [
        "../components/api_server",
        "../components/collector",
        "../components/notifier",
        "../components/shared_code",
        "../docs",
        "../release",
        "../tests/feature_tests",
        "../tests/application_tests",
    ]:
        subprocess.run(("uv", "lock"), cwd=python_project_folder, check=True)
    subprocess.run(("git", "add", "**/uv.lock"), cwd="..", check=True)
    subprocess.run(("git", "commit", "--amend", "--no-edit"), check=True)
    # move the git tag that was just created by bumpversion, instead of figuring it out again
    subprocess.run(("git", "tag", "--force", f"v{get_version()}"), check=True)  # noqa: S603
    if not no_git_push:
        subprocess.run(("git", "push", "--follow-tags"), check=True)


if __name__ == "__main__":
    main()
