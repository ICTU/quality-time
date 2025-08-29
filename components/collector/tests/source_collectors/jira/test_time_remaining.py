"""Unit tests for the Jira time remaining collector."""

from datetime import datetime, timedelta

from .base import JiraTestCase


class JiraTimeRemainingTest(JiraTestCase):
    """Unit tests for the Jira time remaining collector."""

    METRIC_TYPE = "time_remaining"

    def setUp(self):
        """Extend to prepare fake Jira data."""
        super().setUp()
        self.boards_json = {
            "maxResults": 50,
            "startAt": 0,
            "isLast": True,
            "values": [{"id": 2, "name": "Board 2"}],
        }
        self.sprints_json = {
            "values": [
                {
                    "endDate": (datetime.now().astimezone() + timedelta(days=5)).isoformat(),
                    "id": "sprint_id",
                    "originBoardId": "2",
                    "self": "https://jira/rest/agile/1.0/sprint/sprint_id",
                },
            ],
        }

    async def test_end_of_active_sprint(self):
        """Test that the time remaining to the end of the active sprint is returned."""
        get_request_json_side_effect = [self.boards_json, self.sprints_json, self.sprints_json]
        response = await self.collect(get_request_json_side_effect=get_request_json_side_effect)
        expected_landing_url = (
            "https://jira/secure/RapidBoard.jspa?rapidView=2&view=reporting&chart=sprintRetrospective&sprint=sprint_id#"
        )
        self.assert_measurement(response, value="5", landing_url=expected_landing_url, entities=[])
