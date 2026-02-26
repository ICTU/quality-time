"""Unit tests for the Node engine update script."""

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from update_node_engine import update_node_engines


@patch("pathlib.Path.cwd", Mock(return_value=Path("/")))
@patch("logging.Logger.error")
@patch("logging.Logger.warning")
@patch("logging.Logger.info")
@patch("pathlib.Path.rglob")
class UpdateNodeEnginesTest(unittest.TestCase):
    """Unit tests for the update Node engines function."""

    def create_package_json(self, contents: str = '{"engines": {"node": "18" }}') -> Mock:
        """Create a mock package.json file."""
        mock_package_json = Mock(relative_to=Mock(return_value=Mock(parts=[])), read_text=Mock(return_value=contents))
        mock_package_json.parent = Path("/")
        return mock_package_json

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.read_text", Mock(return_value="FROM node:18"))
    def test_unchanged(self, mock_glob: Mock, mock_info: Mock, mock_warning: Mock, mock_error: Mock):
        """Test that the package.json is not written if there is no new Node version."""
        mock_package_json = self.create_package_json()
        mock_glob.return_value = [mock_package_json]
        self.assertEqual(0, update_node_engines())
        mock_info.assert_called_with("Updating %s", mock_package_json.relative_to(), stacklevel=2)
        mock_warning.assert_not_called()
        mock_error.assert_not_called()
        mock_package_json.write_text.assert_not_called()

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.read_text", Mock(return_value="FROM node:19"))
    def test_update(self, mock_glob: Mock, mock_info: Mock, mock_warning: Mock, mock_error: Mock):
        """Test that the package.json is updated if there is a new Node version."""
        mock_package_json = self.create_package_json()
        mock_glob.return_value = [mock_package_json]
        self.assertEqual(0, update_node_engines())
        mock_info.assert_called_with("Updating %s", mock_package_json.relative_to(), stacklevel=2)
        mock_warning.assert_called_with("New version available for %s: %s", "node", "19", stacklevel=2)
        mock_error.assert_not_called()
        mock_package_json.write_text.assert_called_once_with('{"engines": {"node": "19" }}\n')

    def test_no_node_engine(self, mock_glob: Mock, mock_info: Mock, mock_warning: Mock, mock_error: Mock):
        """Test that the package.json is skipped if it has no Node engine."""
        mock_package_json = self.create_package_json("{}")
        mock_glob.return_value = [mock_package_json]
        self.assertEqual(0, update_node_engines())
        mock_info.assert_not_called()
        mock_warning.assert_not_called()
        mock_error.assert_not_called()
        mock_package_json.write_text.assert_not_called()

    @patch("pathlib.Path.exists", Mock(return_value=False))
    def test_no_dockerfile(self, mock_glob: Mock, mock_info: Mock, mock_warning: Mock, mock_error: Mock):
        """Test that an error message is logged if the Dockerfile does not exist."""
        mock_package_json = self.create_package_json()
        mock_glob.return_value = [mock_package_json]
        self.assertEqual(1, update_node_engines())
        mock_info.assert_not_called()
        mock_warning.assert_not_called()
        mock_error.assert_called_with("Expected Dockerfile %s to have a Node base image", Path("/Dockerfile"))
        mock_package_json.write_text.assert_not_called()

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.read_text", Mock(return_value="FROM python:3.14"))
    def test_no_node_base_image(self, mock_glob: Mock, mock_info: Mock, mock_warning: Mock, mock_error: Mock):
        """Test that an error message is logged if the Dockerfile has no Node base image."""
        mock_package_json = self.create_package_json()
        mock_glob.return_value = [mock_package_json]
        self.assertEqual(1, update_node_engines())
        mock_info.assert_not_called()
        mock_warning.assert_not_called()
        mock_error.assert_called_with("Expected Dockerfile %s to have a Node base image", Path("/Dockerfile"))
        mock_package_json.write_text.assert_not_called()
