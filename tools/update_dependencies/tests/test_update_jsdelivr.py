"""Unit tests for the jsdelivr CDN URLs update script."""

import unittest
from unittest.mock import ANY, Mock, patch

from update_jsdelivr import get_latest_version, update_jsdelivr, update_jsdelivrs

from .fixtures import HASH1, HASH2
from .helpers import assert_new_version_logged, assert_path_logged, mock_path, mock_response

# A flat package listing as returned by the jsDelivr API with the ?structure=flat query parameter.
FLAT_FILES = {"default": "/dist/clipboard.min.js", "files": [{"name": "/dist/clipboard.min.js", "hash": HASH2}]}

# The relevant part of the Sphinx config, formatted as Ruff would format it.
CONF = (
    "html_js_files = [\n"
    "    (\n"
    '        "https://cdn.jsdelivr.net/npm/clipboard@2.0.11/dist/clipboard.min.js",\n'
    f'        {{"integrity": "sha256-{HASH1}", "crossorigin": "anonymous"}},\n'
    "    ),\n"
    '    "copy_button.js",\n'
    "]\n"
)


@patch("requests.get")
class GetLatestVersionTest(unittest.TestCase):
    """Unit tests for the get latest jsdelivr version function."""

    def test_unchanged(self, mock_get: Mock):
        """Test that an unchanged version does not fetch an integrity hash."""
        mock_get.side_effect = [
            mock_response({"tags": {"latest": "1.0"}}),
            mock_response({"time": {"1.0": "20260530T10:14:40.567Z"}}),
        ]
        latest_version = get_latest_version("clipboard", "1.0")
        self.assertEqual("1.0", latest_version.version)
        self.assertEqual("", latest_version.sha)

    def test_newer(self, mock_get: Mock):
        """Test that a newer version also fetches the matching integrity hash."""
        mock_get.side_effect = [
            mock_response({"tags": {"latest": "1.1"}}),
            mock_response(FLAT_FILES),
            mock_response({"time": {"1.1": "20260530T10:14:40.567Z"}}),
        ]
        latest_version = get_latest_version("clipboard", "1.0")
        self.assertEqual("1.1", latest_version.version)
        self.assertEqual(f"sha256-{HASH2}", latest_version.sha)

    def test_older(self, mock_get: Mock):
        """Test that an older latest version keeps the current version and does not fetch a hash."""
        mock_get.side_effect = [
            mock_response({"tags": {"latest": "0.9"}}),
            mock_response({"time": {"1.0": "20260530T10:14:40.567Z"}}),
        ]
        latest_version = get_latest_version("clipboard", "1.0")
        self.assertEqual("1.0", latest_version.version)
        self.assertEqual("", latest_version.sha)

    @patch("logging.Logger.error")
    def test_invalid_version(self, mock_error: Mock, mock_get: Mock):
        """Test that an invalid latest version is logged and ignored."""
        mock_get.side_effect = [mock_response({}), mock_response({"time": {"1.0": "20260530T10:14:40.567Z"}})]
        self.assertEqual("1.0", get_latest_version("clipboard", "1.0").version)
        mock_error.assert_called_once_with("Got an invalid version for %s: %s", "clipboard", "''", stacklevel=ANY)


@patch("logging.Logger.warning")
@patch("requests.get")
class UpdateJsdelivrTest(unittest.TestCase):
    """Unit tests for rewriting the version and integrity hash in the Sphinx config."""

    def test_new_version_and_hash(self, mock_get: Mock, mock_warning: Mock):
        """Test that both the version and the integrity hash are updated on a bump."""
        mock_get.side_effect = [
            mock_response({"tags": {"latest": "2.0.12"}}),
            mock_response(FLAT_FILES),
            mock_response({"time": {"2.0.12": "20260530T10:14:40.567Z"}}),
        ]
        new_content = update_jsdelivr(CONF)
        self.assertIn("clipboard@2.0.12/dist/clipboard.min.js", new_content)
        self.assertIn(f'"integrity": "sha256-{HASH2}"', new_content)
        self.assertNotIn("2.0.11", new_content)
        self.assertNotIn(HASH1, new_content)
        assert_new_version_logged(
            mock_warning, "clipboard", "2.0.12, published: 2026-05-30 10:14", "No changelog available!"
        )

    def test_unchanged(self, mock_get: Mock, mock_warning: Mock):
        """Test that the content is unchanged if there is no new version."""
        mock_get.side_effect = [
            mock_response({"tags": {"latest": "2.0.11"}}),
            mock_response({"time": {"2.0.11": "20260530T10:14:40.567Z"}}),
        ]
        self.assertEqual(CONF, update_jsdelivr(CONF))
        mock_warning.assert_not_called()


@patch("logging.Logger.warning")
@patch("logging.Logger.info")
@patch("pathlib.Path.rglob")
@patch("requests.get")
class UpdateJsdelivrsTest(unittest.TestCase):
    """Unit tests for discovering and updating the Sphinx config files under docs/."""

    def test_changes(self, mock_get: Mock, mock_glob: Mock, mock_info: Mock, mock_warning: Mock):
        """Test that a discovered Sphinx config is updated when a new version is available."""
        mock_get.side_effect = [
            mock_response({"tags": {"latest": "2.0.12"}}),
            mock_response(FLAT_FILES),
            mock_response({"time": {"2.0.12": "20260530T10:14:40.567Z"}}),
        ]
        mock_conf = mock_path(CONF)
        mock_glob.return_value = [mock_conf]
        self.assertEqual(0, update_jsdelivrs())
        written = mock_conf.write_text.call_args.args[0]
        self.assertIn("clipboard@2.0.12/dist/clipboard.min.js", written)
        self.assertIn(f'"integrity": "sha256-{HASH2}"', written)
        assert_path_logged(mock_info, mock_conf.relative_to())
        assert_new_version_logged(mock_warning, "clipboard", ANY, ANY)

    def test_no_changes(self, mock_get: Mock, mock_glob: Mock, mock_info: Mock, mock_warning: Mock):
        """Test that a discovered Sphinx config is not rewritten when there is no new version."""
        mock_get.side_effect = [
            mock_response({"tags": {"latest": "2.0.11"}}),
            mock_response({"time": {"2.0.11": "20260530T10:14:40.567Z"}}),
        ]
        mock_conf = mock_path(CONF)
        mock_glob.return_value = [mock_conf]
        self.assertEqual(0, update_jsdelivrs())
        mock_conf.write_text.assert_not_called()
        assert_path_logged(mock_info, mock_conf.relative_to())
        mock_warning.assert_not_called()
