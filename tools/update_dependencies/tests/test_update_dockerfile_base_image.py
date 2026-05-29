"""Unit tests for the Dockerfile base image update script."""

import unittest
from unittest.mock import Mock, patch

from update_dockerfile_base_image import update_dockerfiles

from .fixtures import DIGEST, DIGEST1, DIGEST2
from .helpers import assert_new_version_logged, assert_path_logged, mock_path, mock_response


@patch("logging.Logger.warning")
@patch("logging.Logger.info")
@patch("pathlib.Path.rglob")
@patch("requests.get")
class UpdateDockerfileTest(unittest.TestCase):
    """Unit tests for the update Dockerfile function."""

    def test_no_changes(self, mock_get: Mock, mock_glob: Mock, mock_info: Mock, mock_warning: Mock):
        """Test no changes."""
        mock_get.return_value = mock_response({})
        mock_dockerfile = mock_path(f"FROM node:28.1@{DIGEST}")
        mock_glob.return_value = [mock_dockerfile]
        self.assertEqual(0, update_dockerfiles())
        mock_dockerfile.write_text.assert_not_called()
        assert_path_logged(mock_info, mock_dockerfile.relative_to())
        mock_warning.assert_not_called()

    def test_changes(self, mock_get: Mock, mock_glob: Mock, mock_info: Mock, mock_warning: Mock):
        """Test changes."""
        mock_get.return_value = mock_response({"results": [{"name": "3.15", "digest": DIGEST2}]})
        mock_dockerfile = mock_path(f"FROM python:3.14@{DIGEST1}\n")
        mock_glob.return_value = [mock_dockerfile]
        self.assertEqual(0, update_dockerfiles())
        mock_dockerfile.write_text.assert_called_with(f"FROM python:3.15@{DIGEST2}\n")
        assert_path_logged(mock_info, mock_dockerfile.relative_to())
        assert_new_version_logged(mock_warning, "python", "3.15")
