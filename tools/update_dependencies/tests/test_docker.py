"""Unit tests for the Docker module."""

from datetime import UTC, datetime, timedelta
from unittest.mock import Mock, patch

from docker import get_latest_tag

from .fixtures import DIGEST, DIGEST1, DIGEST2, DIGEST3
from .helpers import CacheClearingTestCase, mock_response


@patch.dict("os.environ", {}, clear=True)
@patch("requests.get")
class GetLatestTagTest(CacheClearingTestCase):
    """Unit tests for getting the latest tag."""

    def test_invalid_current_tag(self, mock_get: Mock):
        """Test that the current tag is returned without querying Docker Hub if it's not a valid version."""
        self.assertEqual("invalid version", get_latest_tag("image", "invalid version").version)
        mock_get.assert_not_called()

    def test_no_results(self, mock_get: Mock):
        """Test that the current tag is returned if Docker Hub has no results."""
        mock_get.return_value = mock_response({})
        self.assertEqual("1.0", get_latest_tag("no_results", "1.0").version)

    def test_empty_results(self, mock_get: Mock):
        """Test that the current tag is returned if Docker Hub has an empty results list."""
        mock_get.return_value = mock_response({"results": []})
        self.assertEqual("1.0", get_latest_tag("empty_results", "1.0").version)

    def test_up_to_date(self, mock_get: Mock):
        """Test that the current tag is returned if it's up to date."""
        mock_get.return_value = mock_response({"results": [{"name": "1.0", "digest": DIGEST}]})
        self.assertEqual("1.0", get_latest_tag("up_to_date", "1.0").version)

    def test_newer(self, mock_get: Mock):
        """Test that the current tag is returned if it's newer than the newest tag available."""
        mock_get.return_value = mock_response({"results": [{"name": "1.0", "digest": DIGEST}]})
        self.assertEqual("1.1", get_latest_tag("newer", "1.1").version)

    def test_new_version_available(self, mock_get: Mock):
        """Test that the new tag is returned if it's newer."""
        mock_get.return_value = mock_response({"results": [{"name": "2.1", "digest": DIGEST}]})
        self.assertEqual("2.1", get_latest_tag("new_version_available", "1.2").version)

    def test_multiple_new_versions_available(self, mock_get: Mock):
        """Test that the newest tag is returned if multiple newer tags are available."""
        mock_get.return_value = mock_response(
            {
                "results": [
                    {"name": "2.2", "digest": DIGEST2},
                    {"name": "2.1", "digest": DIGEST1},
                    {"name": "2.3", "digest": DIGEST3},
                ]
            },
        )
        self.assertEqual("2.3", get_latest_tag("new_versions_available", "1.2").version)

    def test_ignore_tags_without_digest(self, mock_get: Mock):
        """Test that tags without digests are ignored."""
        mock_get.return_value = mock_response({"results": [{"name": "2.2", "digest": DIGEST}, {"name": "2.3"}]})
        self.assertEqual("2.2", get_latest_tag("ignore_tags_without_digest", "1.2").version)

    def test_multiple_new_versions_available_across_pages(self, mock_get: Mock):
        """Test that the newest tag is returned even if the results are paginated."""
        page1 = mock_response(
            {"results": [{"name": "2.1", "digest": DIGEST1}], "next": "https://example.org/next_page"}
        )
        page2 = mock_response({"results": [{"name": "2.2", "digest": DIGEST2}]})
        mock_get.side_effect = [page1, page2]
        self.assertEqual("2.2", get_latest_tag("pagination", "1.2").version)

    def test_invalid_new_tag(self, mock_get: Mock):
        """Test that invalid new tags are ignored."""
        mock_get.return_value = mock_response({"results": [{"name": "invalid", "digest": DIGEST}]})
        self.assertEqual("1.3", get_latest_tag("invalid_new_tag", "1.3").version)

    def test_prerelease(self, mock_get: Mock):
        """Test that prerelease tags are ignored."""
        mock_get.return_value = mock_response({"results": [{"name": "1.4a1", "digest": DIGEST}]})
        self.assertEqual("1.3", get_latest_tag("prerelease", "1.3").version)

    def test_different_suffix(self, mock_get: Mock):
        """Test that tags for different suffixes are ignored."""
        mock_get.return_value = mock_response({"results": [{"name": "1.4-windows", "digest": DIGEST}]})
        self.assertEqual("1.3", get_latest_tag("different_suffix", "1.3").version)

    def test_within_cooldown(self, mock_get: Mock):
        """Test that tags pushed within the cooldown period are ignored."""
        recent = (datetime.now(UTC) - timedelta(days=1)).isoformat()
        mock_get.return_value = mock_response(
            {"results": [{"name": "1.4", "digest": DIGEST, "tag_last_pushed": recent}]}
        )
        self.assertEqual("1.3", get_latest_tag("within_cooldown", "1.3").version)

    def test_outside_cooldown(self, mock_get: Mock):
        """Test that tags pushed before the cooldown period are considered."""
        old = (datetime.now(UTC) - timedelta(days=10)).isoformat()
        mock_get.return_value = mock_response({"results": [{"name": "1.4", "digest": DIGEST, "tag_last_pushed": old}]})
        self.assertEqual("1.4", get_latest_tag("outside_cooldown", "1.3").version)

    @patch.dict("os.environ", {"DOCKER_HUB_USERNAME": "joe_doe", "DOCKER_HUB_TOKEN": "pat123"})  # nosec
    @patch("requests.post")
    def test_user_bearer_token(self, mock_post: Mock, mock_get: Mock):
        """Test that a bearer token is retrieved when Docker Hub credentials are set."""
        mock_get.return_value = mock_response({"results": [{"name": "2.1", "digest": DIGEST}]})
        self.assertEqual("2.1", get_latest_tag("new_version_available_with_credentials", "1.2").version)
        mock_post.assert_called_once_with(
            "https://hub.docker.com/v2/auth/token",
            timeout=10,
            json={"identifier": "joe_doe", "secret": "pat123"},  # nosec
        )
