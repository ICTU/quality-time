"""Unit tests for the Dockerfile base image update script."""

import unittest
from unittest.mock import Mock, patch

from update_dockerfile_base_image import update_dockerfiles

from .fixtures import DIGEST, DIGEST1, DIGEST2


@patch("logging.Logger.warning")
@patch("logging.Logger.info")
@patch("pathlib.Path.rglob")
class UpdateDockerfileTest(unittest.TestCase):
    """Unit tests for the update Dockerfile function."""

    def create_mock_response(self, mock_get: Mock, json: dict) -> None:
        """Create a mock response for the mock requests.get method with the JSON result."""
        response = Mock()
        response.json.return_value = json
        mock_get.return_value = response

    @patch("requests.get")
    def test_no_changes(self, mock_get: Mock, mock_glob: Mock, mock_info: Mock, mock_warning: Mock):
        """Test no changes."""
        self.create_mock_response(mock_get, {})
        mock_dockerfile = Mock(
            relative_to=Mock(return_value=Mock(parts=[])),
            read_text=Mock(return_value=f"FROM node:28.1@{DIGEST}"),
        )
        mock_glob.return_value = [mock_dockerfile]
        self.assertEqual(0, update_dockerfiles())
        mock_dockerfile.write_text.assert_not_called()
        mock_info.assert_called_with("Updating %s", mock_dockerfile.relative_to(), stacklevel=2)
        mock_warning.assert_not_called()

    @patch("requests.get")
    def test_changes(self, mock_get: Mock, mock_glob: Mock, mock_info: Mock, mock_warning: Mock):
        """Test changes."""
        self.create_mock_response(mock_get, {"results": [{"name": "3.15", "digest": DIGEST2}]})
        mock_dockerfile = Mock(
            relative_to=Mock(return_value=Mock(parts=[])),
            read_text=Mock(return_value=f"FROM python:3.14@{DIGEST1}\n"),
        )
        mock_glob.return_value = [mock_dockerfile]
        self.assertEqual(0, update_dockerfiles())
        mock_dockerfile.write_text.assert_called_with(f"FROM python:3.15@{DIGEST2}\n")
        mock_info.assert_called_with("Updating %s", mock_dockerfile.relative_to(), stacklevel=2)
        mock_warning.assert_called_with(
            "New version available for %s: %s\n%s", "python", "3.15", "No changelog available!", stacklevel=2
        )
