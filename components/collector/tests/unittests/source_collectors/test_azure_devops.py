"""Unit tests for the Azure Devops Server (formerly Team Foundation Server) source."""

import unittest
from unittest.mock import Mock, patch

from src.metric_collector import MetricCollector


class AzureDevopsIssuesTest(unittest.TestCase):
    """Unit tests for the Azure Devops Server issues metric."""

    def setUp(self):
        """Test fixture."""
        self.mock_response = Mock()
        self.mock_entity_response = Mock()
        self.work_item = dict(
            id="id", url="http://url",
            fields={"System.TeamProject": "Project", "System.Title": "Title", "System.WorkItemType": "Task",
                    "System.State": "New"})
        self.sources = dict(
            source_id=dict(type="azure_devops", parameters=dict(url="http://azure_devops", private_token="xxx")))
        self.metric = dict(type="issues", sources=self.sources, addition="sum")

    def test_nr_of_issues(self):
        """Test that the number of issues is returned."""
        self.mock_response.json.return_value = dict(workItems=[dict(id="id1"), dict(id="id2")])
        self.mock_entity_response.json.return_value = dict(value=[self.work_item, self.work_item])
        with patch("requests.post", return_value=self.mock_response):
            with patch("requests.get", return_value=self.mock_entity_response):
                response = MetricCollector(self.metric).get()
        self.assertEqual("2", response["sources"][0]["value"])

    def test_no_issues(self):
        """Test zero issues."""
        self.mock_response.json.return_value = dict(workItems=[])
        with patch("requests.post", return_value=self.mock_response):
            with patch("requests.get", return_value=self.mock_entity_response):
                response = MetricCollector(self.metric).get()
        self.assertEqual("0", response["sources"][0]["value"])

    def test_issues(self):
        """Test that the issues are returned."""
        self.mock_response.json.return_value = dict(workItems=[dict(id="id")])
        self.mock_entity_response.json.return_value = dict(value=[self.work_item])
        with patch("requests.post", return_value=self.mock_response):
            with patch("requests.get", return_value=self.mock_entity_response):
                response = MetricCollector(self.metric).get()
        self.assertEqual(
            [dict(key="id", project="Project", title="Title", work_item_type="Task", state="New", url="http://url")],
            response["sources"][0]["entities"])


class AzureDevopsReadyStoryPointsTest(unittest.TestCase):
    """Unit tests for the Azure Devops Server ready story points metric."""

    def setUp(self):
        """Test fixture."""
        self.mock_response = Mock()
        self.mock_entity_response = Mock()
        self.work_item = dict(
            id="id", url="http://url",
            fields={"System.TeamProject": "Project", "System.Title": "Title", "System.WorkItemType": "Task",
                    "System.State": "New", "Microsoft.VSTS.Scheduling.StoryPoints": 2.0})
        self.sources = dict(
            source_id=dict(type="azure_devops", parameters=dict(url="http://azure_devops", private_token="xxx")))
        self.metric = dict(type="ready_user_story_points", sources=self.sources, addition="sum")

    def test_story_points(self):
        """Test that the number of story points are returned."""
        self.mock_response.json.return_value = dict(workItems=[dict(id="id1"), dict(id="id2")])
        self.mock_entity_response.json.return_value = dict(value=[self.work_item, self.work_item])
        with patch("requests.post", return_value=self.mock_response):
            with patch("requests.get", return_value=self.mock_entity_response):
                response = MetricCollector(self.metric).get()
        self.assertEqual("4", response["sources"][0]["value"])

    def test_story_points_without_stories(self):
        """Test that the number of story points is zero when there are no work items."""
        self.mock_response.json.return_value = dict(workItems=[])
        self.mock_entity_response.json.return_value = dict(value=[])
        with patch("requests.post", return_value=self.mock_response):
            with patch("requests.get", return_value=self.mock_entity_response):
                response = MetricCollector(self.metric).get()
        self.assertEqual("0", response["sources"][0]["value"])
