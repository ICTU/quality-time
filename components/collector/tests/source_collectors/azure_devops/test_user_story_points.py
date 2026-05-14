"""Unit tests for the Azure DevOps Server user story points collector."""

from .base import AzureDevopsTestCase


class AzureDevopsUserStoryPointsTest(AzureDevopsTestCase):
    """Unit tests for the Azure DevOps Server user story points metric."""

    METRIC_TYPE = "user_story_points"

    async def test_story_points(self):
        """Test that the number of story points are returned."""
        measurement = await self.collect_measurement(
            post_request_json_side_effect=[
                {"workItems": [{"id": "id1"}, {"id": "id2"}]},
                {"value": [self.work_item, self.work_item]},
            ],
        )
        self.assert_measurement(measurement, value="4")

    async def test_story_points_without_stories(self):
        """Test that the number of story points is zero when there are no work items."""
        measurement = await self.collect_measurement(post_request_json_return_value={"workItems": []})
        self.assert_measurement(measurement, value="0", entities=[])
