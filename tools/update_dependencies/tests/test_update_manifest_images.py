"""Unit tests for the manifest image update script."""

import unittest
from unittest.mock import Mock, patch

from filesystem import YAML_GLOB_PATTERNS
from update_manifest_images import update_manifest_images

from .fixtures import DIGEST, DIGEST1, DIGEST2
from .helpers import assert_new_version_logged, assert_path_logged, mock_path, mock_response


@patch("logging.Logger.warning")
@patch("logging.Logger.info")
@patch("pathlib.Path.rglob")
@patch("requests.get")
class UpdateManifestImagesTest(unittest.TestCase):
    """Unit tests for the update manifest images function."""

    def create_mock_manifest(self, mock_glob: Mock, image: str) -> Mock:
        """Create a mock manifest file with one image line and register it with the path glob mock.

        update_manifest_images globs multiple patterns, so rglob is called once per pattern. A real file matches
        only one glob, so return the mock for the Compose pattern only to avoid processing the same file twice.
        """
        mock_manifest = mock_path(f"    image: {image}\n")
        mock_glob.side_effect = lambda pattern: [mock_manifest] if pattern == "docker-compose*.yml" else []
        return mock_manifest

    def test_no_changes(self, mock_get: Mock, mock_glob: Mock, mock_info: Mock, mock_warning: Mock):
        """Test no changes are made when no newer tag is available."""
        mock_get.return_value = mock_response({})
        mock_manifest = self.create_mock_manifest(mock_glob, f"mongo-express:1.0.2@{DIGEST}")
        self.assertEqual(0, update_manifest_images())
        mock_manifest.write_text.assert_not_called()
        assert_path_logged(mock_info, mock_manifest.relative_to())
        mock_warning.assert_not_called()

    def test_changes(self, mock_get: Mock, mock_glob: Mock, mock_info: Mock, mock_warning: Mock):
        """Test the image tag and digest are bumped when a newer version is available."""
        mock_get.return_value = mock_response({"results": [{"name": "149.0.3", "digest": DIGEST2}]})
        mock_manifest = self.create_mock_manifest(mock_glob, f"selenium/standalone-firefox:149.0.2@{DIGEST1}")
        self.assertEqual(0, update_manifest_images())
        mock_manifest.write_text.assert_called_with(f"    image: selenium/standalone-firefox:149.0.3@{DIGEST2}\n")
        assert_path_logged(mock_info, mock_manifest.relative_to())
        assert_new_version_logged(mock_warning, "selenium/standalone-firefox", "149.0.3")

    def test_variable_substitution_ignored(self, mock_get: Mock, mock_glob: Mock, mock_info: Mock, mock_warning: Mock):
        """Test that image tags using ${...} substitution are not modified."""
        mock_get.return_value = mock_response({"results": [{"name": "999.0"}]})
        mock_manifest = self.create_mock_manifest(mock_glob, "ictu/quality-time_proxy:${QUALITY_TIME_VERSION}")
        self.assertEqual(0, update_manifest_images())
        mock_manifest.write_text.assert_not_called()
        assert_path_logged(mock_info, mock_manifest.relative_to())
        mock_warning.assert_not_called()


@patch("update_manifest_images.update_files", return_value=0)
class ScannedManifestsTest(unittest.TestCase):
    """Unit tests for which manifest files are scanned for pinned images."""

    def test_docker_compose_files_are_scanned(self, mock_update_files: Mock):
        """Test that the Docker Compose files are scanned from the repository root."""
        update_manifest_images()
        compose_call = mock_update_files.call_args_list[0]
        self.assertIn("docker-compose*.yml", compose_call.args)
        self.assertIsNone(compose_call.kwargs.get("start"))

    def test_helm_yaml_files_are_scanned(self, mock_update_files: Mock):
        """Test all YAML files in the Helm folder are scanned, so pinned images stay in sync with Docker Compose."""
        update_manifest_images()
        helm_call = mock_update_files.call_args_list[1]
        self.assertEqual(YAML_GLOB_PATTERNS, helm_call.args)
        self.assertEqual("helm", helm_call.kwargs["start"].name)
