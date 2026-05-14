"""Unit tests for the release script."""

import datetime
import sys
import unittest
from typing import cast
from unittest.mock import ANY, MagicMock, Mock, patch

import release

PYPROJECT_TOML = {
    "tool": {"bumpversion": {"parse": ""}},
    "dependency-groups": {"dev": ["bump-my-version==1.3.0"]},
}


@patch("git.Remote", Mock())
@patch("release.read_pyproject_toml", Mock(return_value=PYPROJECT_TOML))
class MainTest(unittest.TestCase):
    """Unit tests for the main function of the release script."""

    def setUp(self) -> None:
        """Patch the dependencies that every test needs mocked out."""
        self.release_folder = MagicMock()
        cast(Mock, self.release_folder.__str__).return_value = "release_folder"
        self.docs_folder = MagicMock()
        patch("release.RELEASE_FOLDER", self.release_folder).start()
        patch("release.DOCS_FOLDER", self.docs_folder).start()
        self.cwd = patch("pathlib.Path.cwd").start()
        self.cwd.return_value = self.release_folder
        self.repo = patch("git.Repo").start()
        self.mock_run = patch("release.run").start()
        self.addCleanup(patch.stopall)

    def create_tags(self, v1: str = "v1.1.1", v2: str = "v2.2.2") -> list[Mock]:
        """Create mock tags."""
        tag1 = Mock()
        tag1.tag.tag = v1
        tag1.commit.committed_datetime = "2026-05-12T12:00:00Z"
        tag2 = Mock()
        tag2.tag.tag = v2
        tag2.commit.committed_datetime = "2026-05-13T12:00:00Z"
        return [tag1, tag2]

    def prepare_repo(  # noqa: PLR0913
        self,
        repo: Mock,
        *,
        v2: str = "v2.2.2",
        active_branch: str = "master",
        head_commits_match: bool = True,
        is_dirty: bool = False,
        untracked_files: bool = False,
    ) -> None:
        """Prepare the repo mock."""
        repo.return_value = Mock()
        repo.return_value.tags = self.create_tags(v2=v2)
        repo.return_value.heads.master.commit = "commit1"
        repo.return_value.remotes.origin.refs.master.commit = "commit1" if head_commits_match else "commit2"
        repo.return_value.active_branch.name = active_branch
        repo.return_value.is_dirty.return_value = is_dirty
        repo.return_value.untracked_files = ["dirty"] if untracked_files else []

    def changelog(self, contents: str = "[Unreleased]") -> Mock:
        """Create the changelog mock."""
        changelog = MagicMock()
        cast(Mock, changelog.__str__).return_value = "changelog_path"
        changelog.open.return_value.__enter__.return_value.read.return_value = contents
        return changelog

    def versioning_policy(self, version: str = "v1.1.0", date: str = "2026-01-01") -> Mock:
        """Create the versioning policy mock."""
        versioning = MagicMock()
        cast(Mock, versioning.__str__).return_value = "versioning_path"
        versioning.open.return_value.__enter__.return_value.__iter__.return_value = iter(
            [f"| {version} | {date} | extra |\n"],
        )
        return versioning

    def prepare_docs(self, changelog: Mock, versioning: Mock) -> None:
        """Configure the docs folder to return the given changelog and versioning mocks."""
        self.docs_folder.__truediv__.side_effect = lambda name: versioning if name == "versioning.md" else changelog

    def run_main(self, *args: str) -> None:
        """Invoke ``release.main`` with the given CLI arguments."""
        with patch.object(sys, "argv", ["release.py", *args]):
            release.main()

    def assert_version_bumped(self, bump: str) -> None:
        """Assert that bump-my-version was invoked with the given bump argument."""
        self.mock_run.assert_any_call(["uvx", "bump-my-version==1.3.0", "bump", bump], check=True)

    def assert_tag_moved(self, version: str) -> None:
        """Assert that the git tag was re-created at the new commit."""
        self.mock_run.assert_any_call(
            ("git", "tag", "--annotate", "--force", version, "--message", ANY),
            check=True,
        )

    def assert_tag_pushed(self) -> None:
        """Assert that the moved tag was pushed to the remote."""
        self.mock_run.assert_any_call(("git", "push", "--follow-tags"), check=True)

    def assert_tag_not_pushed(self) -> None:
        """Assert that the moved tag was not pushed to the remote."""
        for call in self.mock_run.call_args_list:
            self.assertNotEqual(("git", "push", "--follow-tags"), call.args[0])

    @patch("sys.stderr.write")
    def test_no_args(self, stderr_write: Mock):
        """Test that an error message is shown if the user does not pass any arguments."""
        self.prepare_repo(self.repo)
        with self.assertRaises(SystemExit):
            self.run_main()
        self.assertIn("the following arguments are required: bump", stderr_write.call_args[0][0])

    @patch("release.utc_today", Mock(return_value=datetime.date(2026, 5, 13)))
    def test_bump_without_meeting_preconditions(self):
        """Test that an error message is shown if the preconditions are not met."""
        expected_exit_message = (
            "Please fix these issues before releasing Quality-time:\n"
            "- The current folder is not the release folder. Please change directory to release_folder.\n"
            "- The current branch is not the master branch.\n"
            "- The local HEAD of master (commit1) is not equal to the remote HEAD of master (commit2).\n"
            "- The workspace has uncommitted changes.\n"
            "- The workspace has untracked files.\n"
            "- The changelog (changelog_path) has no '[Unreleased]' header.\n"
            "- The changelog (changelog_path) still contains release candidates; "
            "remove the release candidates and move their changes under the '[Unreleased]' header.\n"
            "- The first line of the version overview table (versioning_path) does not contain "
            "the release date. Expected today: '2026-05-13', found: '2026-01-01'.\n"
            "- The first line of the version overview table (versioning_path) does not contain "
            "the new version. Expected: '2.2.2', found: '1.1.0'.\n"
        )
        self.cwd.return_value = "elsewhere"
        self.prepare_docs(self.changelog("# v1-rc.1"), self.versioning_policy())
        self.prepare_repo(
            self.repo,
            v2="v2.2.2-rc.1",
            active_branch="not master",
            head_commits_match=False,
            is_dirty=True,
            untracked_files=True,
        )
        with self.assertRaises(SystemExit) as system_exit:
            self.run_main("release")
        self.assertEqual(expected_exit_message, system_exit.exception.args[0])

    def test_bump_minor(self):
        """Test bumping the minor version when all preconditions are met."""
        self.prepare_docs(self.changelog(), self.versioning_policy())
        self.prepare_repo(self.repo)
        self.run_main("minor")
        self.assert_version_bumped("minor")
        self.assert_tag_moved("v2.2.2")
        self.assert_tag_pushed()

    @patch("release.utc_today", Mock(return_value=datetime.date(2026, 5, 14)))
    def test_bump_release(self):
        """Test releasing when all preconditions are met."""
        self.prepare_docs(self.changelog(), self.versioning_policy("v2.2.2", "2026-05-14"))
        self.prepare_repo(self.repo, v2="v2.2.2-rc.1")
        self.run_main("release")
        self.assert_version_bumped("pre_release_label")
        self.assert_tag_moved("v2.2.2-rc.1")
        self.assert_tag_pushed()

    @patch("release.utc_today", Mock(return_value=datetime.date(2026, 5, 14)))
    def test_bump_release_check_preconditions(self):
        """Test checking the preconditions before releasing."""
        self.prepare_docs(self.changelog(), self.versioning_policy("v2.2.2", "2026-05-14"))
        self.prepare_repo(self.repo, v2="v2.2.2-rc.1")
        self.run_main("-c", "release")
        self.mock_run.assert_not_called()

    def test_bump_rc(self):
        """Test bumping the release candidate number when all preconditions are met."""
        self.prepare_docs(self.changelog(), self.versioning_policy())
        self.prepare_repo(self.repo, v2="v2.2.2-rc.1")
        self.run_main("rc")
        self.assert_version_bumped("pre_release_number")
        self.assert_tag_moved("v2.2.2-rc.1")
        self.assert_tag_pushed()

    def test_bump_minor_no_git_push(self):
        """Test that --no-git-push skips the final git push."""
        self.prepare_docs(self.changelog(), self.versioning_policy())
        self.prepare_repo(self.repo)
        self.run_main("--no-git-push", "minor")
        self.assert_version_bumped("minor")
        self.assert_tag_moved("v2.2.2")
        self.assert_tag_not_pushed()


class ReadPyprojectTomlTest(unittest.TestCase):
    """Test the read_pyproject_toml function against the real pyproject.toml."""

    def test_read_pyproject_toml(self):
        """Test that read_pyproject_toml parses the release tool's own pyproject.toml."""
        result = release.read_pyproject_toml()
        self.assertIn("tool", result)
        self.assertIn("dependency-groups", result)
