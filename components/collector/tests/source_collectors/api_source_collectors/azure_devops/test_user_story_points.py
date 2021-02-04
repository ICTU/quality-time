"""Unit tests for the Azure Devops Server user story points collector."""

from .base import AzureDevopsTestCase


class AzureDevopsUserStoryPointsTest(AzureDevopsTestCase):
    """Unit tests for the Azure Devops Server user story points metric."""

    def setUp(self):
        """Extend to set up the metric under test."""
        super().setUp()
        self.metric = dict(type="user_story_points", sources=self.sources, addition="sum")

    async def test_story_points(self):
        """Test that the number of story points are returned."""
        response = await self.collect(
            self.metric,
            post_request_json_return_value=dict(workItems=[dict(id="id1"), dict(id="id2")]),
            get_request_json_return_value=dict(value=[self.work_item, self.work_item]),
        )
        self.assert_measurement(response, value="4")

    async def test_story_points_without_stories(self):
        """Test that the number of story points is zero when there are no work items."""
        response = await self.collect(
            self.metric, post_request_json_return_value=dict(workItems=[]), get_request_json_return_value=dict(value=[])
        )
        self.assert_measurement(response, value="0", entities=[])
