"""Unit tests for the Azure Devops Server (formerly Team Foundation Server) source."""

import unittest
from unittest.mock import Mock, patch

from collector.collector import collect_measurement


class AzureDevopsTest(unittest.TestCase):
    """Unit tests for the Azure Devops Server metrics."""

    def setUp(self):
        """Test fixture."""
        self.mock_response = Mock()
        self.sources = dict(
            source_id=dict(type="azure_devops", parameters=dict(url="http://azure_devops", private_token="xxx")))

    def test_nr_of_issues(self):
        """Test that the number of issues is returned."""
        self.mock_response.json.return_value = dict(count=2, results=[])
        metric = dict(type="issues", sources=self.sources)
        with patch("requests.post", return_value=self.mock_response):
            response = collect_measurement(metric)
        self.assertEqual("2", response["sources"][0]["value"])

    def test_issues(self):
        """Test that the issues are returned."""
        self.sources["source_id"]["parameters"]["search_text"] = "text"
        self.sources["source_id"]["parameters"]["work_item_types"] = "User Story"
        self.mock_response.json.return_value = dict(
            count=1,
            results=[
                dict(
                    project=dict(name="Project"),
                    fields={"system.id": "id", "system.workitemtype": "User Story", "system.title": "Title",
                            "system.state": "Active"},
                    url="http://url")])
        metric = dict(type="issues", sources=self.sources)
        with patch("requests.post", return_value=self.mock_response):
            response = collect_measurement(metric)
        self.assertEqual(
            [dict(
                key="id", project="Project", title="Title", work_item_type="User Story", state="Active",
                url="http://url")],
            response["sources"][0]["units"])
