"""Unit tests for the package.json update script."""

import subprocess  # nosec
from pathlib import Path
from unittest.mock import Mock, call, patch

from update_package_json import update_package_jsons

from .helpers import (
    CacheClearingTestCase,
    assert_new_version_logged,
    assert_path_logged,
    mock_path,
    mock_response,
    release_json,
)


@patch("pathlib.Path.cwd", Mock(return_value=Path("/")))
@patch("logging.Logger.warning")
@patch("logging.Logger.info")
@patch("pathlib.Path.rglob")
@patch("subprocess.run")
class UpdatePackageJsonTest(CacheClearingTestCase):
    """Unit tests for the update package.jsons function."""

    def create_package_json(self) -> Mock:
        """Create a mock package.json file."""
        mock_package_json = mock_path("{}")
        mock_package_json.parent = Path("/")
        return mock_package_json

    def assert_npm_called(self, mock_run: Mock) -> None:
        """Assert that npm outdated and npm update have been called."""
        npm_outdated = ["npm", "outdated", "--silent", "--json", "--include=dev"]
        npm_update = ["npm", "update", "--save", "--silent", "--include=dev"]
        run_kwargs = {"capture_output": True, "text": True, "check": True, "cwd": Path("/")}
        mock_run.assert_has_calls((call(npm_outdated, **run_kwargs), call(npm_update, **run_kwargs)))

    def test_unchanged(self, mock_run: Mock, mock_glob: Mock, mock_info: Mock, mock_warning: Mock):
        """Test that the package.json is not written if there are no outdated packages."""
        mock_package_json = self.create_package_json()
        mock_glob.return_value = [mock_package_json]
        mock_run.side_effect = [Mock(stdout="{}"), Mock(stdout="")]
        self.assertEqual(0, update_package_jsons())
        assert_path_logged(mock_info, mock_package_json.relative_to())
        mock_warning.assert_not_called()
        self.assert_npm_called(mock_run)

    @patch(
        "requests.get",
        Mock(
            side_effect=[
                mock_response({"repository": {"url": "https://github.com/package/1.1"}}),
                mock_response([release_json("v1.1", body="Changelog")]),
                mock_response({"time": {"1.1": "20260530T10:26:45.543Z"}}),
                mock_response({"sha": "sha"}),
            ]
        ),
    )
    def test_update(self, mock_run: Mock, mock_glob: Mock, mock_info: Mock, mock_warning: Mock):
        """Test that the package.json is updated if there are outdated packages."""
        mock_package_json = self.create_package_json()
        mock_glob.return_value = [mock_package_json]
        # npm outdated results in a subprocess.CalledProcessError if there are updates:
        mock_run.side_effect = [
            subprocess.CalledProcessError(cmd="", returncode=1, output='{"package": {"latest": "1.1"}}'),
            Mock(stdout=""),
        ]
        self.assertEqual(0, update_package_jsons())
        assert_path_logged(mock_info, mock_package_json.relative_to())
        assert_new_version_logged(mock_warning, "package", "1.1, published: 2026-05-30 10:26", "Changelog")
        self.assert_npm_called(mock_run)
