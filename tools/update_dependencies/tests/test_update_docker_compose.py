"""Unit tests for the Docker Compose file update script."""

import unittest
from unittest.mock import Mock, patch

from update_docker_compose import update_docker_compose_files

from .fixtures import DIGEST, DIGEST1, DIGEST2
from .helpers import assert_new_version_logged, assert_path_logged, mock_path, mock_response


@patch("logging.Logger.warning")
@patch("logging.Logger.info")
@patch("pathlib.Path.rglob")
@patch("requests.get")
class UpdateDockerComposeTest(unittest.TestCase):
    """Unit tests for the update Docker Compose files function."""

    def create_mock_compose(self, mock_glob: Mock, image: str) -> Mock:
        """Create a mock Compose file with one image line and register it with the path glob mock."""
        mock_compose = mock_path(f"    image: {image}\n")
        mock_glob.return_value = [mock_compose]
        return mock_compose

    def test_no_changes(self, mock_get: Mock, mock_glob: Mock, mock_info: Mock, mock_warning: Mock):
        """Test no changes are made when no newer tag is available."""
        mock_get.return_value = mock_response({})
        mock_compose = self.create_mock_compose(mock_glob, f"mongo-express:1.0.2@{DIGEST}")
        self.assertEqual(0, update_docker_compose_files())
        mock_compose.write_text.assert_not_called()
        assert_path_logged(mock_info, mock_compose.relative_to())
        mock_warning.assert_not_called()

    def test_changes(self, mock_get: Mock, mock_glob: Mock, mock_info: Mock, mock_warning: Mock):
        """Test the image tag and digest are bumped when a newer version is available."""
        mock_get.return_value = mock_response({"results": [{"name": "149.0.3", "digest": DIGEST2}]})
        mock_compose = self.create_mock_compose(mock_glob, f"selenium/standalone-firefox:149.0.2@{DIGEST1}")
        self.assertEqual(0, update_docker_compose_files())
        mock_compose.write_text.assert_called_with(f"    image: selenium/standalone-firefox:149.0.3@{DIGEST2}\n")
        assert_path_logged(mock_info, mock_compose.relative_to())
        assert_new_version_logged(mock_warning, "selenium/standalone-firefox", "149.0.3")

    def test_variable_substitution_ignored(self, mock_get: Mock, mock_glob: Mock, mock_info: Mock, mock_warning: Mock):
        """Test that image tags using ${...} substitution are not modified."""
        mock_get.return_value = mock_response({"results": [{"name": "999.0"}]})
        mock_compose = self.create_mock_compose(mock_glob, "ictu/quality-time_proxy:${QUALITY_TIME_VERSION}")
        self.assertEqual(0, update_docker_compose_files())
        mock_compose.write_text.assert_not_called()
        assert_path_logged(mock_info, mock_compose.relative_to())
        mock_warning.assert_not_called()
