"""Unit tests for the Jira metric source."""

import unittest
from unittest.mock import Mock, patch

from src.collector import collect_measurement


class JiraTest(unittest.TestCase):
    """Unit tests for the Jira metrics."""

    def setUp(self):
        self.metric = dict(type="issues", addition="sum",
                           sources=dict(a=dict(type="jira", parameters=dict(url="http://jira", jql="query"))))
        self.mock_response = Mock()

    def test_nr_of_issues(self):
        """Test that the number of issues is returned."""
        self.mock_response.json.return_value = dict(total=42)
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(self.metric)
        self.assertEqual("42", response["sources"][0]["value"])

    def test_issues(self):
        """Test that the issues are returned."""
        self.mock_response.json.return_value = dict(
            total=1, issues=[dict(key="key", id="id", fields=dict(summary="Summary"))])
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(self.metric)
        self.assertEqual(
            [dict(key="id", summary="Summary", url="http://jira/browse/key")],
            response["sources"][0]["entities"])
