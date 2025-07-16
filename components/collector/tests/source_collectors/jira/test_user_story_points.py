"""Unit tests for the Jira user story points collector."""

from model import MetricMeasurement

from .base import JiraTestCase


class JiraUserStoryPointsTest(JiraTestCase):
    """Unit tests for the Jira story points collector."""

    METRIC_TYPE = "user_story_points"

    async def _get_fields_response(self, user_stories_json: dict) -> MetricMeasurement | None | tuple:
        """Produce sprint custom field response."""
        fields_json = [{"name": "Field", "id": "field"}, {"name": "Sprint", "id": "custom_field_001"}]
        return await self.get_response(user_stories_json, fields_json)

    async def test_nr_story_points(self):
        """Test that the number of story points is returned."""
        user_stories_json = {"issues": [self.issue(key="1", field=10), self.issue(key="2", field=32)]}
        response = await self.get_response(user_stories_json)
        self.assert_measurement(
            response,
            value="42",
            entities=[self.entity(key="1", points="10.0"), self.entity(key="2", points="32.0")],
        )

    async def test_nr_story_points_with_sprint_field(self):
        """Test that the number of story points and the sprints are returned, when sprint field is in text format."""
        user_stories_json = {
            "issues": [
                self.issue(key="1", field=10, custom_field_001=["...,state=CLOSED,name=Sprint 1,startDate=..."]),
                self.issue(key="2", field=32, custom_field_001=None),
            ],
        }
        response = await self._get_fields_response(user_stories_json)
        self.assert_measurement(
            response,
            value="42",
            entities=[
                self.entity(key="1", points="10.0", sprint="Sprint 1"),
                self.entity(key="2", points="32.0", sprint=""),
            ],
        )

    async def test_nr_story_points_with_sprint_dict(self):
        """Test that the number of story points and the sprints are returned, when sprint field is in dict format."""
        user_stories_json = {
            "issues": [
                self.issue(key="1", field=10, custom_field_001=[{"id": 1, "name": "Sprint 1", "state": "closed"}]),
                self.issue(key="2", field=32, custom_field_001=None),
            ],
        }
        response = await self._get_fields_response(user_stories_json)
        self.assert_measurement(
            response,
            value="42",
            entities=[
                self.entity(key="1", points="10.0", sprint="Sprint 1"),
                self.entity(key="2", points="32.0", sprint=""),
            ],
        )

    async def test_nr_story_points_without_sprint_text(self):
        """Test that the number of story points and the sprints are returned, when there are no sprints reported."""
        user_stories_json = {
            "issues": [
                self.issue(key="1", field=10, custom_field_001=["There is no spoon"]),
                self.issue(key="2", field=32, custom_field_001=None),
            ],
        }
        response = await self._get_fields_response(user_stories_json)
        self.assert_measurement(
            response,
            value="42",
            entities=[
                self.entity(key="1", points="10.0", sprint=""),
                self.entity(key="2", points="32.0", sprint=""),
            ],
        )

    async def test_nr_story_points_with_mixed_sprints(self):
        """Test that the number of story points and the sprints are returned, when there are mixed sprint fields."""
        user_stories_json = {
            "issues": [
                self.issue(key="1", field=1, custom_field_001=["...,state=CLOSED,name=Sprint 1,startDate=..."]),
                self.issue(key="2", field=2, custom_field_001=["...,state=CLOSED,name=Sprint 1,startDate=..."]),
                self.issue(key="3", field=3, custom_field_001=[{"id": 1, "name": "Sprint 2", "state": "closed"}]),
                self.issue(key="4", field=5, custom_field_001=[{"id": 1, "name": "Sprint 2", "state": "closed"}]),
                self.issue(key="5", field=8, custom_field_001=None),
            ],
        }
        response = await self._get_fields_response(user_stories_json)
        self.assert_measurement(
            response,
            value="19",
            entities=[
                self.entity(key="1", points="1.0", sprint="Sprint 1"),
                self.entity(key="2", points="2.0", sprint="Sprint 1"),
                self.entity(key="3", points="3.0", sprint="Sprint 2"),
                self.entity(key="4", points="5.0", sprint="Sprint 2"),
                self.entity(key="5", points="8.0", sprint=""),
            ],
        )
