"""Unit tests for the Jira metric source."""

import unittest
from unittest.mock import Mock, patch

from src.collector import MetricCollector


class JiraIssuesTest(unittest.TestCase):
    """Unit tests for the Jira issue collector."""

    def setUp(self):
        self.metric = dict(type="issues", addition="sum",
                           sources=dict(a=dict(type="jira", parameters=dict(url="http://jira", jql="query"))))
        self.mock_response = Mock()

    def test_nr_of_issues(self):
        """Test that the number of issues is returned."""
        self.mock_response.json.return_value = dict(total=42)
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(self.metric).get()
        self.assertEqual("42", response["sources"][0]["value"])

    def test_issues(self):
        """Test that the issues are returned."""
        self.mock_response.json.return_value = dict(
            total=1, issues=[dict(key="key", id="id", fields=dict(summary="Summary"))])
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(self.metric).get()
        self.assertEqual(
            [dict(key="id", summary="Summary", url="http://jira/browse/key")],
            response["sources"][0]["entities"])


class JiraReadyUserStoryPointsTest(unittest.TestCase):
    """Unit tests for the Jira ready story points collector."""

    def setUp(self):
        self.metric = dict(
            type="ready_user_story_points", addition="sum",
            sources=dict(
                a=dict(type="jira", parameters=dict(url="http://jira", jql="query", story_points_field="field"))))
        self.mock_response = Mock()

    def test_nr_story_points(self):
        """Test that the number of story points is returned."""
        self.mock_response.json.return_value = dict(
            issues=[
                dict(key="1", id="1", fields=dict(summary="summary 1", field=10)),
                dict(key="2", id="2", fields=dict(summary="summary 2", field=32))])
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(self.metric).get()
        self.assertEqual("42", response["sources"][0]["value"])
