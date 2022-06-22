"""Unit tests for the issue tracker model class."""

import logging
import unittest
from unittest.mock import Mock, patch

from model.issue_tracker import IssueSuggestion, IssueTracker


class IssueTrackerTest(unittest.TestCase):
    """Unit tests for the issue tracker."""

    ISSUE_TRACKER_URL = "https://tracker"
    PROJECT_KEY = "KEY"
    ISSUE_TYPE = "BUG"

    def setUp(self):
        """Override to set up the issue tracker."""
        self.issue_tracker = IssueTracker(self.ISSUE_TRACKER_URL, self.PROJECT_KEY, self.ISSUE_TYPE)

    def test_url(self):
        """Test the issue tracker url."""
        self.assertEqual(self.ISSUE_TRACKER_URL, self.issue_tracker.url)

    def test_username_and_password(self):
        """Test the issue tracker credentials."""
        issue_tracker = IssueTracker(self.ISSUE_TRACKER_URL, self.PROJECT_KEY, self.ISSUE_TYPE, "username", "password")
        self.assertEqual("username", issue_tracker.username)
        self.assertEqual("password", issue_tracker.password)

    def test_private_token(self):
        """Test the issue tracker credentials."""
        issue_tracker = IssueTracker(self.ISSUE_TRACKER_URL, self.PROJECT_KEY, self.ISSUE_TYPE, private_token="token")
        self.assertEqual("token", issue_tracker.private_token)

    @patch("requests.get")
    def test_get_suggestions(self, requests_get):
        """Test that issue suggestions are returned."""
        response = Mock()
        response.json.return_value = dict(issues=[dict(key="FOO-42", fields=dict(summary="Summary"))])
        requests_get.return_value = response
        self.assertEqual([IssueSuggestion("FOO-42", "Summary")], self.issue_tracker.get_suggestions("Summ"))

    def test_get_suggestions_without_url(self):
        """Test that an empty list of issue suggestions is returned."""
        logging.disable(logging.CRITICAL)
        self.assertEqual([], self.issue_tracker.get_suggestions("Query"))
        logging.disable(logging.NOTSET)

    @patch("requests.post")
    def test_create_issue(self, requests_post):
        """Test that an issue can be created."""
        response = Mock()
        response.json.return_value = dict(key="FOO-42")
        requests_post.return_value = response
        self.assertEqual(("FOO-42", ""), self.issue_tracker.create_issue("New issue"))

    def test_create_issue_with_invalid_url(self):
        """Test that without a valid URL an error message is returned."""
        issue_tracker = IssueTracker("invalid", self.PROJECT_KEY, self.ISSUE_TYPE)
        logging.disable(logging.CRITICAL)
        self.assertEqual(
            (
                "",
                "Invalid URL 'invalid/rest/api/2/issue': No scheme supplied. Perhaps you meant "
                "http://invalid/rest/api/2/issue?",
            ),
            issue_tracker.create_issue("New issue"),
        )
        logging.disable(logging.NOTSET)

    def test_create_issue_withoutd_url(self):
        """Test that without a URL an error message is returned."""
        issue_tracker = IssueTracker("", "", "")
        logging.disable(logging.CRITICAL)
        self.assertEqual(("", "Issue tracker has no URL configured."), issue_tracker.create_issue("New issue"))
        logging.disable(logging.NOTSET)
