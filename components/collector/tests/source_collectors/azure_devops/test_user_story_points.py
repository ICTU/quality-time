"""Unit tests for the Azure DevOps Server user story points collector."""

from .base import AzureDevopsTestCase


class AzureDevopsUserStoryPointsTest(AzureDevopsTestCase):
    """Unit tests for the Azure DevOps Server user story points metric."""

    METRIC_TYPE = "user_story_points"

    async def test_story_points(self):
        """Test that the number of story points are returned."""
        response = await self.collect(
            post_request_json_side_effect=[
                dict(workItems=[dict(id="id1"), dict(id="id2")]),
                dict(value=[self.work_item, self.work_item]),
            ]
        )
        self.assert_measurement(response, value="4")

    async def test_story_points_without_stories(self):
        """Test that the number of story points is zero when there are no work items."""
        response = await self.collect(post_request_json_return_value=dict(workItems=[]))
        self.assert_measurement(response, value="0", entities=[])
