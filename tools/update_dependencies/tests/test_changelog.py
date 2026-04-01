"""Unit tests for the changelog parsing."""

import unittest

from changelog import get_version_changes_from_changelog


class GetChangeFromChangelogTest(unittest.TestCase):
    """Unit tests for getting the change for a version from a changelog."""

    def test_empty_changelog(self):
        """Test that an empty changelog results in an empty change."""
        self.assertEqual("", get_version_changes_from_changelog("", "1.0"))

    def test_non_empty_changelog(self):
        """Test that a changelog without the version number simply returns the changelog."""
        self.assertEqual("Empty changelog", get_version_changes_from_changelog("Empty changelog", "1.0"))

    def test_version_number_found(self):
        """Test that a changelog with the version number returns the text after the version number."""
        v1_change = "Version 1.0\n\n- Fixed ...\n- Changed ..."
        changelog = f"Changelog\n\n{v1_change}"
        self.assertEqual(v1_change, get_version_changes_from_changelog(changelog, "1.0"))

    def test_skip_older_versions(self):
        """Test that a older versions are not included."""
        v1_change = "## Version 1.0\n\n- Fixed ...\n- Changed ..."
        changelog = f"Changelog\n\n{v1_change}\n\n## Version 0.9\n\n- Fixed ...\n"
        self.assertEqual(v1_change, get_version_changes_from_changelog(changelog, "1.0"))

    def test_max_length(self):
        """Test the max length."""
        v1_change = "## Version 1.0\n\n- Fixed ...\n- Changed ..."
        text_after_v1 = "# Some other header\n\n- Some bullet point.\n"
        changelog = f"Changelog\n\n{v1_change}\n\n{text_after_v1}"
        expected_v1_change = "## Version 1.0\n\n- Fixed ...\n..."
        self.assertEqual(expected_v1_change, get_version_changes_from_changelog(changelog, "1.0", max_length=3))

    def test_max_length_is_not_applied_when_previous_version_is_found(self):
        """Test that the max length is not applied if the previous version is found."""
        v1_change = "## Version 1.0\n\n- Fixed ...\n- Changed ..."
        changelog = f"Changelog\n\n{v1_change}\n\n## Version 0.9\n\n- Fixed ...\n"
        self.assertEqual(v1_change, get_version_changes_from_changelog(changelog, "1.0", max_length=3))
