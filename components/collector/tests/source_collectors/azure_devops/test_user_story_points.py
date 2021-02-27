"""Unit tests for the Azure Devops Server user story points collector."""

from .base import AzureDevopsTestCase


class AzureDevopsUserStoryPointsTest(AzureDevopsTestCase):
    """Unit tests for the Azure Devops Server user story points metric."""

    METRIC_TYPE = "user_story_points"

    async def test_story_points(self):
        """Test that the number of story points are returned."""
        response = await self.collect(
            get_request_json_return_value=dict(value=[self.work_item, self.work_item]),
            post_request_json_return_value=dict(workItems=[dict(id="id1"), dict(id="id2")]),
        )
        self.assert_measurement(response, value="4.0")

    async def test_story_points_without_stories(self):
        """Test that the number of story points is zero when there are no work items."""
        response = await self.collect(
            get_request_json_return_value=dict(value=[]), post_request_json_return_value=dict(workItems=[])
        )
        self.assert_measurement(response, value="0.0", entities=[])
