"""GitHub unit tests."""

import unittest

from github import github_organization_and_repository, github_to_raw


class GitHubURLtoRawTest(unittest.TestCase):
    """Unit tests for the GitHub URL to raw URL function."""

    def test_non_github_url(self):
        """Test that non-GitHub URLs are unchanged."""
        non_github_url = "https://notgithub.com/blob/example.md"
        self.assertEqual(non_github_url, github_to_raw(non_github_url))

    def test_github_url_with_blob(self):
        """Test that GitHub URLs are changed."""
        github_url = "https://github.com/user/repo/blob/example.md"
        self.assertEqual("https://raw.githubusercontent.com/user/repo/example.md", github_to_raw(github_url))

    def test_github_url_without_blob(self):
        """Test that GitHub URLs are changed."""
        github_url = "https://github.com/user/repo/example.md"
        self.assertEqual("https://raw.githubusercontent.com/user/repo/example.md", github_to_raw(github_url))


class GitHubOrganizationAndRepositoryTest(unittest.TestCase):
    """Unit tests for the GitHub organization and repository parse function."""

    def test_non_github_url(self):
        """Test that non-GitHub URLs return an empty organization and repository."""
        self.assertEqual(("", ""), github_organization_and_repository("https://example.org"))

    def test_github_url(self):
        """Test that a GitHub URLs returns an organization and repository."""
        self.assertEqual(
            ("ICTU", "quality-time"), github_organization_and_repository("https://github.com/ICTU/quality-time")
        )

    def test_github_url_without_repo(self):
        """Test that a GitHub URLs returns an empty organization and repository if the repository is missing."""
        self.assertEqual(("", ""), github_organization_and_repository("https://github.com/ICTU"))
