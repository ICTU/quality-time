"""Unit tests for the issue tracker model class."""

import unittest
from unittest.mock import Mock, patch

from model.issue_tracker import IssueParameters, IssueSuggestion, IssueTracker, IssueTrackerCredentials
from utils.type import URL

from tests.base import disable_logging


class IssueTrackerTest(unittest.TestCase):
    """Unit tests for the issue tracker."""

    ISSUE_TRACKER_URL = URL("https://tracker")
    PROJECT_KEY = "KEY"
    ISSUE_TYPE = "BUG"
    ISSUE_SUMMARY = "Issue summary"

    def issue_tracker(
        self,
        *,
        url: URL | None = None,
        api_version: str = "2",
        credentials: IssueTrackerCredentials | None = None,
        issue_labels: list[str] | None = None,
        epic_link: str = "",
    ) -> IssueTracker:
        """Create an issue tracker."""
        issue_parameters = IssueParameters(self.PROJECT_KEY, self.ISSUE_TYPE, issue_labels, epic_link)
        url = self.ISSUE_TRACKER_URL if url is None else url
        if credentials:
            return IssueTracker(url, api_version, issue_parameters, credentials)
        return IssueTracker(url, api_version, issue_parameters)

    def test_url(self):
        """Test the issue tracker url."""
        self.assertEqual(self.ISSUE_TRACKER_URL, self.issue_tracker().url)

    def test_username_and_password(self):
        """Test the issue tracker credentials."""
        credentials = IssueTrackerCredentials("username", "password")
        issue_tracker = self.issue_tracker(credentials=credentials)
        self.assertEqual("username", issue_tracker.credentials.username)
        self.assertEqual("password", issue_tracker.credentials.password)

    def test_private_token(self):
        """Test the issue tracker credentials."""
        credentials = IssueTrackerCredentials(private_token="token")  # nosec
        issue_tracker = self.issue_tracker(credentials=credentials)
        self.assertEqual("token", issue_tracker.credentials.private_token)

    def test_issue_labels(self):
        """Test the issue tracker issue labels."""
        issue_tracker = self.issue_tracker(issue_labels=["Label"])
        self.assertEqual(["Label"], issue_tracker.issue_parameters.issue_labels)

    def test_issue_epic_link(self):
        """Test the issue tracker epic link."""
        issue_tracker = self.issue_tracker(epic_link="FOO-42")
        self.assertEqual("FOO-42", issue_tracker.issue_parameters.epic_link)

    @patch("requests.get")
    def test_get_suggestions_with_api_v2(self, requests_get):
        """Test that issue suggestions are returned when the API version is v2."""
        response = Mock()
        response.json.return_value = {"issues": [{"key": "FOO-42", "fields": {"summary": self.ISSUE_SUMMARY}}]}
        requests_get.return_value = response
        expected_suggestions = [IssueSuggestion("FOO-42", "Issue summary")]
        self.assertEqual(expected_suggestions, self.issue_tracker(api_version="2").get_suggestions("Summ"))

    @patch("requests.get")
    def test_get_suggestions_with_api_v3(self, requests_get):
        """Test that issue suggestions are returned when the API version is v3."""
        response = Mock()
        response.json.return_value = {"issues": [{"key": "FOO-42", "fields": {"summary": self.ISSUE_SUMMARY}}]}
        requests_get.return_value = response
        expected_suggestions = [IssueSuggestion("FOO-42", "Issue summary")]
        self.assertEqual(expected_suggestions, self.issue_tracker(api_version="3").get_suggestions("Summ"))

    @disable_logging
    def test_get_suggestions_without_url(self):
        """Test that an empty list of issue suggestions is returned."""
        self.assertEqual([], self.issue_tracker().get_suggestions("Query"))

    @patch("requests.post")
    def test_create_issue_with_v2(self, requests_post: Mock):
        """Test that an issue can be created with v2 of the API."""
        response = Mock()
        response.json.return_value = {"key": "FOO-42"}
        requests_post.return_value = response
        self.assertEqual(
            ("FOO-42", ""),
            self.issue_tracker(api_version="2").create_issue("Summary", "Description [link|https://example.org]."),
        )
        requests_post.assert_called_with(
            self.ISSUE_TRACKER_URL + "/rest/api/2/issue",
            auth=None,
            headers={},
            json={
                "fields": {
                    "project": {"key": self.PROJECT_KEY},
                    "issuetype": {"name": self.ISSUE_TYPE},
                    "summary": "Summary",
                    "description": "Description [link|https://example.org].",
                }
            },
            timeout=10,
        )

    @patch("requests.post")
    def test_create_issue_with_v3(self, requests_post: Mock):
        """Test that an issue can be created with v3 of the API."""
        response = Mock()
        response.json.return_value = {"key": "FOO-42"}
        requests_post.return_value = response
        self.assertEqual(
            ("FOO-42", ""),
            self.issue_tracker(api_version="3").create_issue("Summary", "Description [link|https://example.org]."),
        )
        requests_post.assert_called_with(
            self.ISSUE_TRACKER_URL + "/rest/api/3/issue",
            auth=None,
            headers={},
            json={
                "fields": {
                    "project": {"key": self.PROJECT_KEY},
                    "issuetype": {"name": self.ISSUE_TYPE},
                    "summary": "Summary",
                    "description": {
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {"text": "Description ", "marks": [], "type": "text"},
                                    {
                                        "type": "text",
                                        "text": "link",
                                        "marks": [{"attrs": {"href": "https://example.org"}, "type": "link"}],
                                    },
                                    {"text": ".", "marks": [], "type": "text"},
                                ],
                            }
                        ],
                        "type": "doc",
                        "version": 1,
                    },
                }
            },
            timeout=10,
        )

    @disable_logging
    def test_create_issue_with_invalid_url(self):
        """Test that without a valid URL an error message is returned."""
        issue_tracker = self.issue_tracker(url=URL("invalid"))
        self.assertIn(
            issue_tracker.create_issue("New issue"),
            [
                (
                    "",
                    "Invalid URL 'invalid/rest/api/2/issue': No scheme supplied. Perhaps you meant "
                    "https://invalid/rest/api/2/issue?",
                ),
                (
                    "",
                    "Invalid URL 'invalid/rest/api/2/issue': No scheme supplied. Perhaps you meant "
                    "http://invalid/rest/api/2/issue?",  # Python <3.11 and Windows
                ),
            ],
        )

    @disable_logging
    def test_create_issue_without_url(self):
        """Test that without a URL an error message is returned."""
        issue_tracker = self.issue_tracker(url=URL(""))
        self.assertEqual(("", "Issue tracker has no URL configured."), issue_tracker.create_issue(self.ISSUE_SUMMARY))

    @disable_logging
    @patch("requests.post")
    def test_create_issue_with_exception(self, requests_post):
        """Test that the exception is returned when something goes wrong."""
        requests_post.side_effect = [OSError("Something went wrong")]
        self.assertEqual(("", "Something went wrong"), self.issue_tracker().create_issue(self.ISSUE_SUMMARY))

    @disable_logging
    @patch("requests.post")
    def test_create_issue_with_empty_exception(self, requests_post):
        """Test that the exception is returned when something goes wrong."""
        requests_post.side_effect = [OSError]
        self.assertEqual(("", "OSError"), self.issue_tracker().create_issue(self.ISSUE_SUMMARY))
