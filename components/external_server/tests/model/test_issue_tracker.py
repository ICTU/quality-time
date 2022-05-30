"""Unit tests for the issue tracker model class."""

import logging
import unittest
from unittest.mock import Mock, patch

from model.issue_tracker import IssueSuggestion, IssueTracker


class IssueTrackerTest(unittest.TestCase):
    """Unit tests for the issue tracker."""

    ISSUE_TRACKER_URL = "https://tracker"

    def test_url(self):
        """Test the issue tracker url."""
        self.assertEqual(self.ISSUE_TRACKER_URL, IssueTracker(self.ISSUE_TRACKER_URL).url)

    def test_username_and_password(self):
        """Test the issue tracker credentials."""
        issue_tracker = IssueTracker(self.ISSUE_TRACKER_URL, "username", "password")
        self.assertEqual("username", issue_tracker.username)
        self.assertEqual("password", issue_tracker.password)

    def test_private_token(self):
        """Test the issue tracker credentials."""
        issue_tracker = IssueTracker(self.ISSUE_TRACKER_URL, private_token="token")
        self.assertEqual("token", issue_tracker.private_token)

    @patch("requests.get")
    def test_get_suggestions(self, requests_get):
        """Test that issue suggestions are returned."""
        response = Mock()
        response.json.return_value = dict(sections=[dict(issues=[dict(key="FOO-42", summaryText="Summary")])])
        requests_get.return_value = response
        issue_tracker = IssueTracker(self.ISSUE_TRACKER_URL)
        self.assertEqual([IssueSuggestion("FOO-42", "Summary")], issue_tracker.get_suggestions("Summ"))

    def test_get_suggestions_without_url(self):
        """Test that an empty list of issue suggestions is returned."""
        issue_tracker = IssueTracker("")
        logging.disable(logging.CRITICAL)
        self.assertEqual([], issue_tracker.get_suggestions("Query"))
        logging.disable(logging.NOTSET)
