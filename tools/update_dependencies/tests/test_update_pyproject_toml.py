"""Unit tests for the pyproject.toml update script."""

from pathlib import Path
from typing import TYPE_CHECKING, ClassVar
from unittest.mock import Mock, patch

from update_pyproject_toml import update_pyproject_tomls

from .helpers import (
    CacheClearingTestCase,
    assert_new_version_logged,
    assert_path_logged,
    mock_path,
    mock_response,
    release_json,
)

if TYPE_CHECKING:
    from pypi import Release


@patch("pathlib.Path.cwd", Mock(return_value=Path("/")))
@patch("logging.Logger.warning")
@patch("logging.Logger.info")
@patch("pathlib.Path.rglob")
@patch("requests.get")
@patch("subprocess.run")
class UpdatePyprojectTomlsTest(CacheClearingTestCase):
    """Unit tests for the update pyproject.tomls function."""

    changelog: ClassVar = "Changelog"

    @staticmethod
    def pypi_metadata(
        changelog_url: str = "https://changelog",
        repository: str = "https://github.com/repo/package_with_github_releases",
    ) -> Release:
        """Create PyPI release metadata fixture."""
        project_urls = {"Homepage": "https://home", "repository": repository}
        if changelog_url:
            project_urls["Changelog"] = changelog_url
        return {
            "info": {"description": "Package description", "project_urls": project_urls},
            "urls": [{"upload_time_iso_8601": "2026-05-30T12:07:03.123456Z"}],
        }

    def create_pyproject_toml(self, contents: str) -> Mock:
        """Create a mock pyproject.toml file."""
        mock_pyproject_toml = mock_path(contents)
        mock_pyproject_toml.parent = Path("/")
        return mock_pyproject_toml

    def mock_update_on_stdout(self, package: str, latest: str = "") -> Mock:
        """Mock stdout with optional package update."""
        update = f" (latest: {latest})" if latest else ""
        return Mock(stdout=f"| {package}{update}\n")

    def test_update(self, run: Mock, get: Mock, glob: Mock, info: Mock, warning: Mock):
        """Test updating a pyproject.toml."""
        run.return_value = self.mock_update_on_stdout("package", "v1.1")
        get.return_value = mock_response(
            {"info": {"description": "Package"}, "urls": [{"upload_time_iso_8601": "2026-05-30T12:08:53.123321Z"}]}
        )
        mock_pyproject_toml = self.create_pyproject_toml('"package==1.0"\n')
        glob.return_value = [mock_pyproject_toml]
        self.assertEqual(0, update_pyproject_tomls())
        mock_pyproject_toml.write_text.assert_called_with('"package==1.1"\n')
        assert_path_logged(info, Path("uv.lock"))
        assert_new_version_logged(warning, "package", "1.1, published: 2026-05-30 12:08")

    def test_update_with_changelog(self, run: Mock, get: Mock, glob: Mock, info: Mock, warning: Mock):
        """Test updating a pyproject.toml with changelog."""
        run.return_value = self.mock_update_on_stdout("package_with_changelog", "v1.1")
        get.side_effect = [
            mock_response(self.pypi_metadata()),
            Mock(headers={"Content-Type": "text"}, text=self.changelog),
        ]
        mock_pyproject_toml = self.create_pyproject_toml('"package_with_changelog==1.0"\n')
        glob.return_value = [mock_pyproject_toml]
        self.assertEqual(0, update_pyproject_tomls())
        mock_pyproject_toml.write_text.assert_called_with('"package_with_changelog==1.1"\n')
        assert_path_logged(info, Path("uv.lock"))
        assert_new_version_logged(warning, "package_with_changelog", "1.1, published: 2026-05-30 12:07", self.changelog)

    def test_update_with_html_changelog(self, run: Mock, get: Mock, glob: Mock, info: Mock, warning: Mock):
        """Test that updating a pyproject.toml with only a HTML changelog ignores the changelog."""
        run.return_value = self.mock_update_on_stdout("package_with_html_changelog", "v1.1")
        get.side_effect = [
            mock_response(self.pypi_metadata()),
            Mock(text=self.changelog, headers={"Content-Type": "text/html"}),
            mock_response([{"tag_name": "v1.1"}]),
        ]
        mock_pyproject_toml = self.create_pyproject_toml('"package_with_html_changelog==1.0"\n')
        glob.return_value = [mock_pyproject_toml]
        self.assertEqual(0, update_pyproject_tomls())
        mock_pyproject_toml.write_text.assert_called_with('"package_with_html_changelog==1.1"\n')
        assert_path_logged(info, Path("uv.lock"))
        assert_new_version_logged(warning, "package_with_html_changelog", "1.1, published: 2026-05-30 12:07")

    def test_update_with_github_url(self, run: Mock, get: Mock, glob: Mock, info: Mock, warning: Mock):
        """Test updating a pyproject.toml with GitHub releases."""
        run.return_value = self.mock_update_on_stdout("package_with_github_releases", "v1.1")
        get.side_effect = [
            mock_response(self.pypi_metadata(changelog_url="")),
            mock_response([release_json("v1.1", body=self.changelog)]),
            mock_response({"sha": "sha"}),
        ]
        mock_pyproject_toml = self.create_pyproject_toml('"package_with_github_releases==1.0"\n')
        glob.return_value = [mock_pyproject_toml]
        self.assertEqual(0, update_pyproject_tomls())
        mock_pyproject_toml.write_text.assert_called_with('"package_with_github_releases==1.1"\n')
        assert_path_logged(info, Path("uv.lock"))
        assert_new_version_logged(
            warning, "package_with_github_releases", "1.1, published: 2026-05-30 12:07", self.changelog
        )

    def test_update_without_github_url(self, run: Mock, get: Mock, glob: Mock, info: Mock, warning: Mock):
        """Test updating a pyproject.toml without a GitHub URL."""
        run.return_value = self.mock_update_on_stdout("package_without_github_releases", "v1.1")
        get.return_value = mock_response(self.pypi_metadata(changelog_url="", repository="https://gitlab.com/org/repo"))
        mock_pyproject_toml = self.create_pyproject_toml('"package_without_github_releases==1.0"\n')
        glob.return_value = [mock_pyproject_toml]
        self.assertEqual(0, update_pyproject_tomls())
        mock_pyproject_toml.write_text.assert_called_with('"package_without_github_releases==1.1"\n')
        assert_path_logged(info, Path("uv.lock"))
        assert_new_version_logged(warning, "package_without_github_releases", "1.1, published: 2026-05-30 12:07")

    def test_unchanged(self, run: Mock, get: Mock, glob: Mock, info: Mock, warning: Mock):
        """Test that the pyproject.toml is not written if there are no changes."""
        run.return_value = self.mock_update_on_stdout("package")
        mock_pyproject_toml = self.create_pyproject_toml('"package==1.0"\n')
        glob.return_value = [mock_pyproject_toml]
        self.assertEqual(0, update_pyproject_tomls())
        mock_pyproject_toml.write_text.assert_not_called()
        assert_path_logged(info, Path("uv.lock"))
        get.assert_not_called()
        warning.assert_not_called()
