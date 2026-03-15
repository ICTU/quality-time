"""Unit tests for the changelog."""

import re
import unittest
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar

from packaging.version import Version


class ChangelogTest(unittest.TestCase):
    """Tests for the changelog."""

    version_header_re = r"## v(?P<version>\d+\.\d+\.(?P<patch>\d+)) - (?P<date>\d{4}-\d{2}-\d{2})$"
    changelog_lines: ClassVar[list[str]] = []

    @classmethod
    def setUpClass(cls) -> None:
        """Read the changelog."""
        cls.changelog_lines = Path("src/changelog.md").read_text(encoding="utf-8").splitlines()

    def test_allowed_headers(self):
        """Test that sections only have allowed headers."""
        allowed_patch_headers = ("Changed", "Deployment notes", "Fixed", "Removed")
        allowed_non_patch_headers = ("Added", "Changed", "Deployment notes", "Deprecated", "Fixed", "Removed")
        in_patch = False
        last_version = ""
        for line in self.changelog_lines:
            if match := re.match(self.version_header_re, line):
                last_version = line
                in_patch = int(match.group("patch")) > 0
            if line.startswith("### ") and last_version != "## [Unreleased]":
                allowed_headers = allowed_patch_headers if in_patch else allowed_non_patch_headers
                self.assertIn(line.removeprefix("### "), allowed_headers, last_version)

    def test_version_header_format(self):
        """Test that version headers have the correct format."""
        for line in self.changelog_lines:
            if line.startswith("## ") and line not in {"## [Unreleased]", "## Note before upgrading"}:
                self.assertRegex(line, self.version_header_re)

    def test_dates(self):
        """Test that version header dates are in descending order and not in the future."""
        current_date = datetime.now(tz=UTC).astimezone().date().isoformat()
        for line in self.changelog_lines:
            if match := re.match(self.version_header_re, line):
                previous_date, current_date = current_date, match.group("date")
                self.assertGreaterEqual(previous_date, current_date)

    def test_version(self):
        """Test that versions are in descending order."""
        current_version = Version("9999.9999.9999")
        for line in self.changelog_lines:
            if match := re.match(self.version_header_re, line):
                previous_version, current_version = current_version, Version(match.group("version"))
                self.assertGreater(previous_version, current_version)

    def test_no_duplicate_headers(self):
        """Test that headers are not duplicated."""
        headers = set()
        for line in self.changelog_lines:
            if line.startswith("### "):
                self.assertNotIn(line, headers)
                headers.add(line)
            elif line.startswith("#"):
                headers = set()

    def test_no_empty_sections(self):
        """Test that sections are not empty."""
        section_contents = ""
        for line in self.changelog_lines:
            if line.startswith("### "):
                self.assertNotEqual("", section_contents)
                section_contents = ""
            else:
                section_contents += line
        self.assertNotEqual("", section_contents)  # Check last section

    def test_that_sections_have_bullet_points(self):
        """Test that sections only have bullet points or continuation lines."""
        in_version_section = False
        for line in self.changelog_lines:
            if line == "### Deployment notes":
                in_version_section = False
            elif line.startswith("### "):
                in_version_section = True
            elif line.startswith("#"):
                in_version_section = False
            elif in_version_section and line:
                self.assertStartsWith(line, ("- ", "  "), line)

    def test_unreleased_section(self):
        """Test that the unreleased section, if any, comes before version headers."""
        first_version_seen = False
        for line in self.changelog_lines:
            if re.match(self.version_header_re, line):
                first_version_seen = True
            if first_version_seen:
                self.assertNotEqual(line, "## [Unreleased]")
