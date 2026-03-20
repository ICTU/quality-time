"""Unit tests for the pyproject.toml update script."""

import unittest
from pathlib import Path
from typing import ClassVar
from unittest.mock import Mock, patch

from update_pyproject_toml import update_pyproject_tomls


@patch("pathlib.Path.cwd", Mock(return_value=Path("/")))
@patch("logging.Logger.warning")
@patch("logging.Logger.info")
@patch("pathlib.Path.rglob")
class UpdatePyprojectTomlsTest(unittest.TestCase):
    """Unit tests for the update pyproject.tomls function."""

    changelog: ClassVar = "Changelog"

    @staticmethod
    def pypi_metadata(
        changelog_url: str = "https://changelog",
        repository: str = "https://github.com/repo/package_with_github_releases",
    ) -> dict[str, dict[str, dict[str, str]]]:
        """Create PyPI metadata fixture."""
        project_urls = {"Homepage": "https://home", "repository": repository}
        if changelog_url:
            project_urls["Changelog"] = changelog_url
        return {"info": {"project_urls": project_urls}}

    def create_pyproject_toml(self) -> Mock:
        """Create a mock pyproject.toml file."""
        mock_pyproject_toml = Mock(
            relative_to=Mock(return_value=Mock(parts=[])),
            read_text=Mock(
                return_value=""""package==1.0"
"package_with_changelog==1.0"
"package_with_github_releases==1.0"
"package_without_github_releases==1.0"
"""
            ),
        )
        mock_pyproject_toml.parent = Path("/")
        return mock_pyproject_toml

    @patch("requests.get", Mock(return_value=Mock(json=Mock(return_value={"info": {}}))))
    @patch("subprocess.run", Mock(return_value=Mock(stdout="| package (latest: v1.1)\n")))
    def test_update(self, mock_glob: Mock, mock_info: Mock, mock_warning: Mock):
        """Test updating a pyproject.toml."""
        mock_pyproject_toml = self.create_pyproject_toml()
        mock_glob.return_value = [mock_pyproject_toml]
        self.assertEqual(0, update_pyproject_tomls())
        mock_pyproject_toml.write_text.assert_called_with(
            """"package==1.1"
"package_with_changelog==1.0"
"package_with_github_releases==1.0"
"package_without_github_releases==1.0"
"""
        )
        mock_info.assert_called_with("Updating %s", Path("uv.lock"), stacklevel=2)
        mock_warning.assert_called_with(
            "New version available for %s: %s\n%s", "package", "1.1", "No changelog available!", stacklevel=2
        )

    @patch("requests.get", Mock(side_effect=[Mock(json=Mock(return_value=pypi_metadata())), Mock(text=changelog)]))
    @patch("subprocess.run", Mock(return_value=Mock(stdout="| package_with_changelog (latest: v1.1)\n")))
    def test_update_with_changelog(self, mock_glob: Mock, mock_info: Mock, mock_warning: Mock):
        """Test updating a pyproject.toml with changelog."""
        mock_pyproject_toml = self.create_pyproject_toml()
        mock_glob.return_value = [mock_pyproject_toml]
        self.assertEqual(0, update_pyproject_tomls())
        mock_pyproject_toml.write_text.assert_called_with(
            """"package==1.0"
"package_with_changelog==1.1"
"package_with_github_releases==1.0"
"package_without_github_releases==1.0"
"""
        )
        mock_info.assert_called_with("Updating %s", Path("uv.lock"), stacklevel=2)
        mock_warning.assert_called_with(
            "New version available for %s: %s\n%s", "package_with_changelog", "1.1", self.changelog, stacklevel=2
        )

    @patch(
        "requests.get",
        Mock(
            side_effect=[
                Mock(json=Mock(return_value=pypi_metadata(changelog_url=""))),
                Mock(json=Mock(return_value={"body": changelog})),
            ]
        ),
    )
    @patch("subprocess.run", Mock(return_value=Mock(stdout="| package_with_github_releases (latest: v1.1)\n")))
    def test_update_with_github_url(self, mock_glob: Mock, mock_info: Mock, mock_warning: Mock):
        """Test updating a pyproject.toml with GitHub releases."""
        mock_pyproject_toml = self.create_pyproject_toml()
        mock_glob.return_value = [mock_pyproject_toml]
        self.assertEqual(0, update_pyproject_tomls())
        mock_pyproject_toml.write_text.assert_called_with(
            """"package==1.0"
"package_with_changelog==1.0"
"package_with_github_releases==1.1"
"package_without_github_releases==1.0"
"""
        )
        mock_info.assert_called_with("Updating %s", Path("uv.lock"), stacklevel=2)
        mock_warning.assert_called_with(
            "New version available for %s: %s\n%s", "package_with_github_releases", "1.1", self.changelog, stacklevel=2
        )

    @patch(
        "requests.get",
        Mock(
            return_value=Mock(
                json=Mock(return_value=pypi_metadata(changelog_url="", repository="https://gitlab.com/org/repo"))
            ),
        ),
    )
    @patch("subprocess.run", Mock(return_value=Mock(stdout="| package_without_github_releases (latest: v1.1)\n")))
    def test_update_without_github_url(self, mock_glob: Mock, mock_info: Mock, mock_warning: Mock):
        """Test updating a pyproject.toml without a GitHub URL."""
        mock_pyproject_toml = self.create_pyproject_toml()
        mock_glob.return_value = [mock_pyproject_toml]
        self.assertEqual(0, update_pyproject_tomls())
        mock_pyproject_toml.write_text.assert_called_with(
            """"package==1.0"
"package_with_changelog==1.0"
"package_with_github_releases==1.0"
"package_without_github_releases==1.1"
"""
        )
        mock_info.assert_called_with("Updating %s", Path("uv.lock"), stacklevel=2)
        mock_warning.assert_called_with(
            "New version available for %s: %s\n%s",
            "package_without_github_releases",
            "1.1",
            "No changelog available!",
            stacklevel=2,
        )

    @patch("subprocess.run", Mock(return_value=Mock(stdout="| package\n")))
    def test_unchanged(self, mock_glob: Mock, mock_info: Mock, mock_warning: Mock):
        """Test that the pyproject.toml is not written if there are no changes."""
        mock_pyproject_toml = self.create_pyproject_toml()
        mock_glob.return_value = [mock_pyproject_toml]
        self.assertEqual(0, update_pyproject_tomls())
        mock_pyproject_toml.write_text.assert_not_called()
        mock_info.assert_called_with("Updating %s", Path("uv.lock"), stacklevel=2)
        mock_warning.assert_not_called()
