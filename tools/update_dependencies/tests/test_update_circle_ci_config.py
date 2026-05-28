"""Unit tests for the Circle CI config update script."""

import unittest
from unittest.mock import Mock, patch

from update_circle_ci_config import update_circle_ci_config

from .fixtures import DIGEST, DIGEST1, DIGEST2


@patch("logging.Logger.warning")
@patch("logging.Logger.info")
@patch("requests.get")
class UpdateCircleCIConfigTest(unittest.TestCase):
    """Unit tests for the update Circle CI config function."""

    def create_mock_response(self, mock_get: Mock, json: dict) -> None:
        """Create a mock response for the mock requests.get method with the JSON result."""
        response = Mock()
        response.json.return_value = json
        mock_get.return_value = response

    def test_no_changes(self, mock_get: Mock, mock_info: Mock, mock_warning: Mock):
        """Test no changes."""
        self.create_mock_response(mock_get, {})
        config_yml = Mock(read_text=Mock(return_value=f"image: cimg/node:26.8@{DIGEST}\n"))
        self.assertEqual(0, update_circle_ci_config(config_yml))
        config_yml.write_text.assert_not_called()
        mock_info.assert_called_with("Updating %s", config_yml.relative_to(), stacklevel=2)
        mock_warning.assert_not_called()

    def test_changes(self, mock_get: Mock, mock_info: Mock, mock_warning: Mock):
        """Test the image tag and digest are bumped when a newer version is available."""
        self.create_mock_response(mock_get, {"results": [{"name": "3.14.2", "digest": DIGEST2}]})
        config_yml = Mock(read_text=Mock(return_value=f"image: cimg/py:3.14.1@{DIGEST1}\n"))
        self.assertEqual(0, update_circle_ci_config(config_yml))
        config_yml.write_text.assert_called_with(f"image: cimg/py:3.14.2@{DIGEST2}\n")
        mock_info.assert_called_with("Updating %s", config_yml.relative_to(), stacklevel=2)
        mock_warning.assert_called_with(
            "New version available for %s: %s\n%s", "cimg/py", "3.14.2", "No changelog available!", stacklevel=2
        )

    def test_machine_executor_alias_ignored(self, mock_get: Mock, mock_info: Mock, mock_warning: Mock):
        """Test that machine-executor 'image: default' aliases without a tag are not modified."""
        self.create_mock_response(mock_get, {"results": [{"name": "3.14.2", "digest": DIGEST}]})
        config_yml = Mock(read_text=Mock(return_value="image: default\n"))
        self.assertEqual(0, update_circle_ci_config(config_yml))
        config_yml.write_text.assert_not_called()
        mock_info.assert_called_with("Updating %s", config_yml.relative_to(), stacklevel=2)
        mock_warning.assert_not_called()
