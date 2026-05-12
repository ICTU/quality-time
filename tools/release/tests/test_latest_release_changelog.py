"""Unit tests for generating the latest release changelog."""

import pathlib
import unittest
from unittest.mock import mock_open, patch

from latest_release_changelog import latest_release


class LatestReleaseTest(unittest.TestCase):
    """Unit tests for getting the changes for the latest release."""

    def get_latest_release(self, changelog: str) -> str:
        """Return the latest release from the changelog."""
        with patch.object(pathlib.Path, "open", mock_open(read_data=changelog)):
            return latest_release(pathlib.Path("changelog.md"))

    def test_empty_changelog(self):
        """Test that an empty changelog results in an empty change."""
        changelog = "# Changelog\n## [Unreleased]\n"
        expected_changelog = ""
        self.assertEqual(expected_changelog, self.get_latest_release(changelog))

    def test_one_release(self):
        """Test that the newest release is listed."""
        changelog = "# Changelog\n\n## v1.0\n\n### Added\n\n- Some feature"
        expected_changelog = "# v1.0\n\n## Added\n\n- Some feature"
        self.assertEqual(expected_changelog, self.get_latest_release(changelog))

    def test_two_releases(self):
        """Test that only the newest release is listed."""
        changelog = "# Changelog\n\n## v1.0\n\n### Added\n\n- Some feature\n\n## v0.9\n\n### Added\n\n- Feature"
        expected_changelog = "# v1.0\n\n## Added\n\n- Some feature\n\n"
        self.assertEqual(expected_changelog, self.get_latest_release(changelog))
