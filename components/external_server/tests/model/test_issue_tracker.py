"""Unit tests for the issue tracker model class."""

import unittest
from unittest.mock import Mock, patch

from model.issue_tracker import IssueParameters, IssueSuggestion, IssueTracker, IssueTrackerCredentials

from tests.base import disable_logging


class IssueTrackerTest(unittest.TestCase):
    """Unit tests for the issue tracker."""

    ISSUE_TRACKER_URL = "https://tracker"
    PROJECT_KEY = "KEY"
    ISSUE_TYPE = "BUG"
    ISSUE_SUMMARY = "Issue summary"

    def setUp(self):
        """Override to set up the issue tracker."""
        self.issue_parameters = IssueParameters(self.PROJECT_KEY, self.ISSUE_TYPE)
        self.issue_tracker = IssueTracker(self.ISSUE_TRACKER_URL, self.issue_parameters)

    def test_url(self):
        """Test the issue tracker url."""
        self.assertEqual(self.ISSUE_TRACKER_URL, self.issue_tracker.url)

    def test_username_and_password(self):
        """Test the issue tracker credentials."""
        credentials = IssueTrackerCredentials("username", "password")
        issue_tracker = IssueTracker(self.ISSUE_TRACKER_URL, self.issue_parameters, credentials)
        self.assertEqual("username", issue_tracker.credentials.username)
        self.assertEqual("password", issue_tracker.credentials.password)

    def test_private_token(self):
        """Test the issue tracker credentials."""
        credentials = IssueTrackerCredentials(private_token="token")
        issue_tracker = IssueTracker(self.ISSUE_TRACKER_URL, self.issue_parameters, credentials)
        self.assertEqual("token", issue_tracker.credentials.private_token)

    def test_issue_labels(self):
        """Test the issue tracker issue labels."""
        self.issue_parameters.issue_labels = ["Label"]
        issue_tracker = IssueTracker(self.ISSUE_TRACKER_URL, self.issue_parameters)
        self.assertEqual(["Label"], issue_tracker.issue_parameters.issue_labels)

    def test_issue_epic_link(self):
        """Test the issue tracker epic link."""
        self.issue_parameters.epic_link = "FOO-42"
        issue_tracker = IssueTracker(self.ISSUE_TRACKER_URL, self.issue_parameters)
        self.assertEqual("FOO-42", issue_tracker.issue_parameters.epic_link)

    @patch("requests.get")
    def test_get_suggestions(self, requests_get):
        """Test that issue suggestions are returned."""
        response = Mock()
        response.json.return_value = {"issues": [{"key": "FOO-42", "fields": {"summary": self.ISSUE_SUMMARY}}]}
        requests_get.return_value = response
        self.assertEqual([IssueSuggestion("FOO-42", "Issue summary")], self.issue_tracker.get_suggestions("Summ"))

    @disable_logging
    def test_get_suggestions_without_url(self):
        """Test that an empty list of issue suggestions is returned."""
        self.assertEqual([], self.issue_tracker.get_suggestions("Query"))

    @patch("requests.post")
    def test_create_issue(self, requests_post):
        """Test that an issue can be created."""
        response = Mock()
        response.json.return_value = {"key": "FOO-42"}
        requests_post.return_value = response
        self.assertEqual(("FOO-42", ""), self.issue_tracker.create_issue(self.ISSUE_SUMMARY))

    @disable_logging
    def test_create_issue_with_invalid_url(self):
        """Test that without a valid URL an error message is returned."""
        issue_tracker = IssueTracker("invalid", self.issue_parameters)
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
        issue_tracker = IssueTracker("", self.issue_parameters)
        self.assertEqual(("", "Issue tracker has no URL configured."), issue_tracker.create_issue(self.ISSUE_SUMMARY))
