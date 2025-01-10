"""Unit tests for the SonarQube todo and fixme comments collector."""

from .base import SonarQubeTestCase


class SonarQubeTodoAndFixmeCommentsTest(SonarQubeTestCase):
    """Unit tests for the SonarQube todo and fixme comments collector."""

    METRIC_TYPE = "todo_and_fixme_comments"

    async def test_todo_and_fixme_comments(self):
        """Test that the number of todo and fixme comments is returned."""
        json = {"total": "2"}
        response = await self.collect(get_request_json_return_value=json)
        self.assert_measurement(
            response,
            value="2",
            total="100",
            landing_url=f"{self.issues_landing_url}&rules={self.sonar_rules('todo_and_fixme_comment')}",
        )
