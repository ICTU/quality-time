"""Unit tests for the Jira user story points collector."""

from .base import JiraTestCase


class JiraUserStoryPointsTest(JiraTestCase):
    """Unit tests for the Jira story points collector."""

    METRIC_TYPE = "user_story_points"

    async def test_nr_story_points(self):
        """Test that the number of story points is returned."""
        user_stories_json = dict(issues=[self.issue(key="1", field=10), self.issue(key="2", field=32)])
        response = await self.get_response(user_stories_json)
        self.assert_measurement(
            response, value="42", entities=[self.entity(key="1", points="10.0"), self.entity(key="2", points="32.0")]
        )

    async def test_nr_story_points_with_sprint_field(self):
        """Test that the number of story points and the sprints are returned."""
        user_stories_json = dict(
            issues=[
                self.issue(key="1", field=10, custom_field_001=["...,state=CLOSED,name=Sprint 1,startDate=..."]),
                self.issue(key="2", field=32, custom_field_001=None),
            ]
        )
        fields_json = [dict(name="Sprint", id="custom_field_001")]
        response = await self.get_response(user_stories_json, fields_json)
        self.assert_measurement(
            response,
            value="42",
            entities=[
                self.entity(key="1", points="10.0", sprint="Sprint 1"),
                self.entity(key="2", points="32.0", sprint=""),
            ],
        )
