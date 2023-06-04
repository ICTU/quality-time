"""Unit tests for the Jira average issue lead time collector."""

from .base import JiraTestCase


class JiraAverageIssueLeadTimeTest(JiraTestCase):
    """Unit tests for the Jira average issue lead time collector."""

    METRIC_TYPE = "average_issue_lead_time"

    async def test_value(self):
        """Test that the lead time of issues are returned."""
        self.set_source_parameter("lookback_days", "424242")
        updated_value = "2020-08-09T16:36:48.000+0200"
        status_issue = self.issue(status={"statusCategory": {"key": "done"}}, updated=updated_value)
        issues_json = {"total": 1, "issues": [status_issue]}
        response = await self.get_response(issues_json)
        self.assert_measurement(response, value="3", entities=[self.entity(updated=updated_value, lead_time=3)])

    async def test_exclude_status_category(self):
        """Test that issues are excluded if statusCategory is not done."""
        self.set_source_parameter("lookback_days", "424242")
        updated_value = "2020-08-09T16:36:48.000+0200"
        status_issue = self.issue(status={"statusCategory": {"key": "todo"}}, updated=updated_value)
        issues_json = {"total": 0, "issues": [status_issue]}
        response = await self.get_response(issues_json)
        self.assert_measurement(response, value="0", entities=[])

    async def test_exclude_updated_field(self):
        """Test that issues are excluded if there is no field updated."""
        self.set_source_parameter("lookback_days", "424242")
        status_issue = self.issue(
            status={"statusCategory": {"key": "done"}},
        )
        issues_json = {"total": 0, "issues": [status_issue]}
        response = await self.get_response(issues_json)
        self.assert_measurement(response, value="0", entities=[])
