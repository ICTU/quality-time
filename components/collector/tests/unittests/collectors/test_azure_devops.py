"""Unit tests for the Azure Devops Server (formerly Team Foundation Server) source."""

import unittest
from unittest.mock import Mock, patch

from src.collector import collect_measurement


class AzureDevopsTest(unittest.TestCase):
    """Unit tests for the Azure Devops Server metrics."""

    def setUp(self):
        """Test fixture."""
        self.mock_response = Mock()
        self.mock_unit_response = Mock()
        self.work_item = dict(
            id="id", url="http://url",
            fields={"System.TeamProject": "Project", "System.Title": "Title", "System.WorkItemType": "Task",
                    "System.State": "New"})
        self.sources = dict(
            source_id=dict(type="azure_devops", parameters=dict(url="http://azure_devops", private_token="xxx")))

    def test_nr_of_issues(self):
        """Test that the number of issues is returned."""
        self.mock_response.json.return_value = dict(workItems=[dict(id="id1"), dict(id="id2")])
        self.mock_unit_response.json.return_value = dict(value=[self.work_item, self.work_item])
        metric = dict(type="issues", sources=self.sources)
        with patch("requests.post", return_value=self.mock_response):
            with patch("requests.get", return_value=self.mock_unit_response):
                response = collect_measurement(metric)
        self.assertEqual("2", response["sources"][0]["value"])

    def test_no_issues(self):
        """Test zero issues."""
        self.mock_response.json.return_value = dict(workItems=[])
        metric = dict(type="issues", sources=self.sources)
        with patch("requests.post", return_value=self.mock_response):
            with patch("requests.get", return_value=self.mock_unit_response):
                response = collect_measurement(metric)
        self.assertEqual("0", response["sources"][0]["value"])

    def test_issues(self):
        """Test that the issues are returned."""
        self.mock_response.json.return_value = dict(workItems=[dict(id="id")])
        self.mock_unit_response.json.return_value = dict(value=[self.work_item])
        metric = dict(type="issues", sources=self.sources)
        with patch("requests.post", return_value=self.mock_response):
            with patch("requests.get", return_value=self.mock_unit_response):
                response = collect_measurement(metric)
        self.assertEqual(
            [dict(key="id", project="Project", title="Title", work_item_type="Task", state="New", url="http://url")],
            response["sources"][0]["units"])
