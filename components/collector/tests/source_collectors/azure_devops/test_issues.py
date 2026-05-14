"""Unit tests for the Azure DevOps Server issues collector."""

from unittest.mock import ANY

from .base import AzureDevopsTestCase


class AzureDevopsIssuesTest(AzureDevopsTestCase):
    """Unit tests for the Azure DevOps Server issues metric."""

    METRIC_TYPE = "issues"

    async def test_nr_of_issues(self):
        """Test that the number of issues is returned."""
        measurement = await self.collect_measurement(
            post_request_json_side_effect=[
                {"workItems": [{"id": "id1"}, {"id": "id2"}]},
                {"value": [self.work_item, self.work_item]},
            ],
        )
        self.assert_measurement(measurement, value="2")

    async def test_no_issues(self):
        """Test zero issues."""
        measurement = await self.collect_measurement(post_request_json_return_value={"workItems": []})
        self.assert_measurement(measurement, value="0", entities=[])

    async def test_empty_issue_response(self):
        """Test that value is taken from workItems total call, instead of empty item response json."""
        ret_value = [{"workItems": [{"id": "id"}]}, None]  # needed for line coverage in source_collector_test_case.py
        measurement = await self.collect_measurement(
            post_request_json_return_value=ret_value, post_request_json_side_effect=ret_value
        )
        self.assert_measurement(measurement, value="1", entities=[])

    async def test_wiql_with_where(self):
        """Test wiql parameter is used."""
        self.set_source_parameter("wiql", "WHERE 1")
        _, _, post_mock = await self.collect_measurement_and_mocks(post_request_json_return_value={"workItems": []})
        post_mock.assert_called_once_with(ANY, auth=ANY, json={"query": "Select [System.Id] From WorkItems WHERE 1"})

    async def test_wiql_without_where(self):
        """Test wiql parameter is used."""
        self.set_source_parameter("wiql", "42")
        _, _, post_mock = await self.collect_measurement_and_mocks(post_request_json_return_value={"workItems": []})
        post_mock.assert_called_once_with(ANY, auth=ANY, json={"query": "Select [System.Id] From WorkItems WHERE 42"})

    async def test_issues(self):
        """Test that the issues are returned."""
        measurement = await self.collect_measurement(
            post_request_json_side_effect=[{"workItems": [{"id": "id"}]}, {"value": [self.work_item]}],
        )
        self.assert_measurement(
            measurement,
            entities=[
                {
                    "key": "id",
                    "project": "Project",
                    "title": "Title",
                    "work_item_type": "Task",
                    "state": "New",
                    "url": self.work_item_url,
                },
            ],
        )
