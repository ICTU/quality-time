"""Unit tests for the pyproject.toml update script."""

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from update_pyproject_toml import update_pyproject_tomls


@patch("pathlib.Path.cwd", Mock(return_value=Path("/")))
@patch("logging.Logger.warning")
@patch("logging.Logger.info")
@patch("pathlib.Path.rglob")
class UpdatePyprojectTomlsTest(unittest.TestCase):
    """Unit tests for the update project.tomls function."""

    def create_pyproject_toml(self) -> Mock:
        """Create a mock pyproject.toml file."""
        mock_pyproject_toml = Mock(
            relative_to=Mock(return_value=Mock(parts=[])),
            read_text=Mock(return_value='"package==1.0"\n'),
        )
        mock_pyproject_toml.parent = Path("/")
        return mock_pyproject_toml

    @patch("subprocess.run", Mock(return_value=Mock(stdout="| package (latest: v1.1)\n")))
    def test_update(self, mock_glob: Mock, mock_info: Mock, mock_warning: Mock):
        """Test updating a pyproject.toml."""
        mock_pyproject_toml = self.create_pyproject_toml()
        mock_glob.return_value = [mock_pyproject_toml]
        update_pyproject_tomls()
        mock_pyproject_toml.write_text.assert_called_with('"package==1.1"\n')
        mock_info.assert_called_with("Updating %s", Path("uv.lock"), stacklevel=2)
        mock_warning.assert_called_with("New version available for %s: %s", "package", "1.1", stacklevel=2)

    @patch("subprocess.run", Mock(return_value=Mock(stdout="| package\n")))
    def test_unchanged(self, mock_glob: Mock, mock_info: Mock, mock_warning: Mock):
        """Test that the pyproject.toml is not written if there are no changes."""
        mock_pyproject_toml = self.create_pyproject_toml()
        mock_glob.return_value = [mock_pyproject_toml]
        update_pyproject_tomls()
        mock_pyproject_toml.write_text.assert_not_called()
        mock_info.assert_called_with("Updating %s", Path("uv.lock"), stacklevel=2)
        mock_warning.assert_not_called()
