"""GitHub unit tests."""

import unittest
from unittest.mock import Mock, patch

import requests

from github import get_latest_release_json, github_organization_and_repository, github_to_raw


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


class GitHubReleaseJSONTest(unittest.TestCase):
    """Unit tests for getting the latest release JSON for a GitHub repo."""

    # Note get_latest_release_json uses caching, so the organization and/or reponeed to be difficult for each test

    @patch("requests.get", Mock(return_value=Mock(json=Mock(return_value={"tag_name": "1.0"}))))
    def test_get_latest_release_json(self):
        """Test getting the latest release JSON."""
        self.assertEqual({"tag_name": "1.0"}, get_latest_release_json("organization", "repository"))

    @patch("requests.get")
    def test_get_latest_release_json_when_repo_has_no_releases(self, mock_get: Mock):
        """Test getting the latest release JSON when the repository has no releases."""
        mock_get.return_value = Mock(raise_for_status=Mock(side_effect=requests.exceptions.HTTPError))
        self.assertEqual({}, get_latest_release_json("organization", "repository without releases"))
