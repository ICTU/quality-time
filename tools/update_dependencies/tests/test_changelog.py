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

    def test_prose_mention_of_version_does_not_anchor_parsing(self):
        """Test that a prose mention of the version in a newer section doesn't anchor parsing there."""
        v2_change = "## [2.0.0]\n\n- A feature, completing the work started in 1.0.0."
        v1_change = "## [1.0.0]\n\n- Fixed ...\n- Changed ..."
        changelog = f"# Changelog\n\n{v2_change}\n\n{v1_change}\n\n## [0.9.0]\n\n- Fixed ...\n"
        self.assertEqual(v1_change, get_version_changes_from_changelog(changelog, "1.0.0"))

    def test_repeated_prose_mention_without_heading_anchors_on_first(self):
        """Test that without a heading, parsing anchors on the first of several prose mentions."""
        changelog = "Upgrade to 1.0.0 is recommended.\nThe 1.0.0 release fixes things."
        self.assertEqual(changelog, get_version_changes_from_changelog(changelog, "1.0.0"))

    def test_version_in_footer_link_does_not_anchor_parsing(self):
        """Test that a version mention in a footer comparison link doesn't anchor parsing there."""
        v1_change = "## [1.0.0]\n\n- Fixed ...\n- Changed ..."
        footer = "[1.0.0]: https://example.org/compare/v0.9.0...v1.0.0"
        changelog = f"# Changelog\n\n{v1_change}\n\n## [0.9.0]\n\n- Fixed ...\n\n{footer}\n"
        self.assertEqual(v1_change, get_version_changes_from_changelog(changelog, "1.0.0"))
