"""Unit tests for the Azure DevOps Server issues collector."""

from .base import AzureDevopsTestCase


class AzureDevopsIssuesTest(AzureDevopsTestCase):
    """Unit tests for the Azure DevOps Server issues metric."""

    METRIC_TYPE = "issues"

    async def test_nr_of_issues(self):
        """Test that the number of issues is returned."""
        response = await self.collect(post_request_json_side_effect=[
            dict(workItems=[dict(id="id1"), dict(id="id2")]),
            dict(value=[self.work_item, self.work_item])
        ])
        self.assert_measurement(response, value="2")

    async def test_no_issues(self):
        """Test zero issues."""
        response = await self.collect(post_request_json_return_value=dict(workItems=[]))
        self.assert_measurement(response, value="0", entities=[])

    async def test_issues(self):
        """Test that the issues are returned."""
        response = await self.collect(post_request_json_side_effect=[
            dict(workItems=[dict(id="id")]),
            dict(value=[self.work_item])
        ])
        self.assert_measurement(
            response,
            entities=[
                dict(
                    key="id",
                    project="Project",
                    title="Title",
                    work_item_type="Task",
                    state="New",
                    url=self.work_item_url,
                )
            ],
        )
