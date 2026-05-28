"""GitHub unit tests."""

import unittest
from datetime import UTC, datetime, timedelta
from typing import cast
from unittest.mock import Mock, patch

import requests

from github import Release, get_latest_release, get_release, github_owner_and_repository, github_to_raw

from .helpers import mock_response


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


class GitHubOwnerAndRepositoryTest(unittest.TestCase):
    """Unit tests for the GitHub owner and repository parse function."""

    def test_non_github_url(self):
        """Test that non-GitHub URLs return an empty owner and repository."""
        self.assertEqual(("", ""), github_owner_and_repository("https://example.org"))

    def test_github_url(self):
        """Test that a GitHub URLs returns an owner and repository."""
        self.assertEqual(("ICTU", "quality-time"), github_owner_and_repository("https://github.com/ICTU/quality-time"))

    def test_github_url_without_repo(self):
        """Test that a GitHub URLs returns an empty owner and repository if the repository is missing."""
        self.assertEqual(("", ""), github_owner_and_repository("https://github.com/ICTU"))


class GetLatestReleaseTest(unittest.TestCase):
    """Unit tests for getting the latest release for a GitHub repo."""

    # Note get_latest_release uses caching, so the owner and/or repository need to be different for each test

    @patch("requests.get")
    def test_get_latest_release(self, mock_get: Mock):
        """Test getting the latest release."""
        mock_get.side_effect = [
            mock_response([{"draft": False, "prerelease": False, "tag_name": "1.0"}]),
            mock_response({"sha": "sha"}),
        ]
        release = get_latest_release("owner", "repository")
        self.assertEqual(Release(owner="owner", repository="repository", tag_name="1.0"), release)
        self.assertEqual("sha", cast("Release", release).commit_sha)

    @patch("requests.get")
    def test_get_latest_release_when_repo_has_no_releases(self, mock_get: Mock):
        """Test getting the latest release when the repository has no releases."""
        mock_get.return_value = Mock(raise_for_status=Mock(side_effect=requests.exceptions.HTTPError))
        self.assertIsNone(get_latest_release("owner", "repository without releases"))

    @patch("requests.get", Mock(return_value=mock_response([{"draft": True, "prerelease": False, "tag_name": "1.0"}])))
    def test_skip_draft_releases(self):
        """Test that draft releases are not included."""
        self.assertIsNone(get_latest_release("owner", "repository with only a draft release"))

    @patch("requests.get", Mock(return_value=mock_response([{"draft": False, "prerelease": True, "tag_name": "1.0"}])))
    def test_skip_prerelease_releases(self):
        """Test that prerelease releases are not included."""
        self.assertIsNone(get_latest_release("owner", "repository with only a prerelease release"))

    @patch(
        "requests.get",
        Mock(return_value=mock_response([{"draft": False, "prerelease": False, "tag_name": "invalid-1.0"}])),
    )
    def test_invalid_versions(self):
        """Test that invalid versions are not included."""
        self.assertIsNone(get_latest_release("owner", "repository with a invalid version"))

    @patch("logging.Logger.error")
    @patch("requests.get")
    def test_http_error_on_commits_endpoint(self, mock_get: Mock, mock_error: Mock):
        """Test that reading commit_sha returns an empty string and logs an error when the commits endpoint fails."""
        mock_get.side_effect = [
            mock_response([{"draft": False, "prerelease": False, "tag_name": "1.0"}]),
            Mock(raise_for_status=Mock(side_effect=requests.exceptions.HTTPError)),
        ]
        release = get_latest_release("owner", "repository 2")
        self.assertIsNotNone(release)
        self.assertIsNone(cast("Release", release).commit_sha)
        mock_error.assert_called_once_with(
            "Could not fetch commit SHA for %s %s: %s",
            "owner/repository 2",
            "1.0",
            "https://github.com/owner/repository 2/releases/tag/1.0",
            stacklevel=2,
        )

    @patch("requests.get")
    def test_skip_releases_within_cooldown(self, mock_get: Mock):
        """Test that releases published within the cooldown period are skipped in favor of older releases."""
        recent = (datetime.now(UTC) - timedelta(days=1)).isoformat()
        old_iso = (datetime.now(UTC) - timedelta(days=10)).isoformat()
        mock_get.return_value = mock_response(
            [
                {"draft": False, "prerelease": False, "tag_name": "2.0", "published_at": recent},
                {"draft": False, "prerelease": False, "tag_name": "1.0", "published_at": old_iso},
            ]
        )
        release = get_latest_release("owner", "repository with cooldown")
        self.assertEqual(
            Release(
                owner="owner",
                repository="repository with cooldown",
                tag_name="1.0",
                published_at=datetime.fromisoformat(old_iso),
            ),
            release,
        )


class GetReleaseTest(unittest.TestCase):
    """Unit tests for getting a release matching a specific package and version."""

    # Note _list_releases uses caching, so the owner and/or repository need to be different for each test

    @patch("requests.get")
    def test_monorepo_tag_match(self, mock_get: Mock):
        """Test finding a release in a monorepo where tags are prefixed with the package name."""
        mock_get.return_value = mock_response(
            [
                {"draft": False, "prerelease": False, "tag_name": "puppeteer-v25.1.0"},
                {"draft": False, "prerelease": False, "tag_name": "puppeteer-core-v25.0.4", "body": "Changelog"},
            ]
        )
        release = get_release("puppeteer", "monorepo", "puppeteer-core", "25.0.4")
        self.assertEqual("puppeteer-core-v25.0.4", cast("Release", release).tag_name)
        self.assertEqual("Changelog", cast("Release", release).body)

    @patch(
        "requests.get",
        Mock(return_value=mock_response([{"draft": False, "prerelease": False, "tag_name": "v1.2.3"}])),
    )
    def test_v_prefix_tag_match(self):
        """Test finding a release whose tag is the version prefixed with 'v'."""
        release = get_release("owner", "repo with v prefix", "any", "1.2.3")
        self.assertEqual("v1.2.3", cast("Release", release).tag_name)

    @patch(
        "requests.get",
        Mock(return_value=mock_response([{"draft": False, "prerelease": False, "tag_name": "1.2.3"}])),
    )
    def test_bare_version_tag_match(self):
        """Test finding a release whose tag is the bare version."""
        release = get_release("owner", "repo with bare version", "any", "1.2.3")
        self.assertEqual("1.2.3", cast("Release", release).tag_name)

    @patch(
        "requests.get",
        Mock(return_value=mock_response([{"draft": False, "prerelease": False, "tag_name": "v1.0"}])),
    )
    def test_no_matching_tag(self):
        """Test that None is returned when no tag matches the requested version."""
        self.assertIsNone(get_release("owner", "repo with non matching tag", "any", "1.1"))

    @patch("requests.get")
    def test_repo_without_releases(self, mock_get: Mock):
        """Test that None is returned when the repository can't be reached."""
        mock_get.return_value = Mock(raise_for_status=Mock(side_effect=requests.exceptions.HTTPError))
        self.assertIsNone(get_release("owner", "repo without releases for get_release", "any", "1.0"))
