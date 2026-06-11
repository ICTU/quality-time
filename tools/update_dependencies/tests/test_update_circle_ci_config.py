"""Unit tests for the Circle CI config update script."""

from pathlib import Path
from unittest.mock import Mock, patch

from update_circle_ci_config import update_circle_ci_config

from .fixtures import DIGEST, DIGEST1, DIGEST2
from .helpers import CacheClearingTestCase, assert_new_version_logged, assert_path_logged, mock_path, mock_response

CIRCLE_CI_DIR = Path("/repo/.circleci")


@patch("logging.Logger.warning")
@patch("logging.Logger.info")
@patch("requests.get")
@patch("pathlib.Path.glob")
class UpdateCircleCIConfigTest(CacheClearingTestCase):
    """Unit tests for the update Circle CI config function."""

    def test_no_changes(self, mock_glob: Mock, mock_get: Mock, mock_info: Mock, mock_warning: Mock):
        """Test no changes."""
        mock_get.return_value = mock_response({})
        config_yml = mock_path(f"image: cimg/node:26.8@{DIGEST}\n")
        mock_glob.side_effect = [[config_yml], []]
        self.assertEqual(0, update_circle_ci_config(CIRCLE_CI_DIR))
        config_yml.write_text.assert_not_called()
        assert_path_logged(mock_info, config_yml.relative_to())
        mock_warning.assert_not_called()

    def test_changes(self, mock_glob: Mock, mock_get: Mock, mock_info: Mock, mock_warning: Mock):
        """Test the image tag and digest are bumped when a newer version is available."""
        mock_get.return_value = mock_response({"results": [{"name": "3.14.2", "digest": DIGEST2}]})
        config_yml = mock_path(f"image: cimg/py:3.14.1@{DIGEST1}\n")
        mock_glob.side_effect = [[config_yml], []]
        self.assertEqual(0, update_circle_ci_config(CIRCLE_CI_DIR))
        config_yml.write_text.assert_called_with(f"image: cimg/py:3.14.2@{DIGEST2}\n")
        assert_path_logged(mock_info, config_yml.relative_to())
        assert_new_version_logged(mock_warning, "cimg/py", "3.14.2")

    def test_multiple_files(self, mock_glob: Mock, mock_get: Mock, mock_info: Mock, mock_warning: Mock):
        """Test that images are updated in all YAML files under the CircleCI directory, not just config.yml."""
        mock_get.return_value = mock_response({"results": [{"name": "1.26.2", "digest": DIGEST2}]})
        config_yml = mock_path(f"image: cimg/go:1.26.1@{DIGEST1}\n")
        continue_yaml = mock_path(f"image: cimg/go:1.26.1@{DIGEST1}\n")
        mock_glob.side_effect = [[config_yml], [continue_yaml]]
        self.assertEqual(0, update_circle_ci_config(CIRCLE_CI_DIR))
        config_yml.write_text.assert_called_with(f"image: cimg/go:1.26.2@{DIGEST2}\n")
        continue_yaml.write_text.assert_called_with(f"image: cimg/go:1.26.2@{DIGEST2}\n")
        assert_path_logged(mock_info, continue_yaml.relative_to())
        self.assertEqual(2, mock_warning.call_count)
        assert_new_version_logged(mock_warning, "cimg/go", "1.26.2", "Suppressing changelog already shown, see above")

    def test_machine_executor_alias_ignored(self, mock_glob: Mock, mock_get: Mock, mock_info: Mock, mock_warning: Mock):
        """Test that machine-executor 'image: default' aliases without a tag are not modified."""
        mock_get.return_value = mock_response({"results": [{"name": "3.14.2", "digest": DIGEST}]})
        config_yml = mock_path("image: default\n")
        mock_glob.side_effect = [[config_yml], []]
        self.assertEqual(0, update_circle_ci_config(CIRCLE_CI_DIR))
        config_yml.write_text.assert_not_called()
        assert_path_logged(mock_info, config_yml.relative_to())
        mock_warning.assert_not_called()
