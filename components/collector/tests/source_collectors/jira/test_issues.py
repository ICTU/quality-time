"""Unit tests for the Jira issues collector."""

from .base import JiraTestCase


class JiraIssuesTest(JiraTestCase):
    """Unit tests for the Jira issue collector."""

    METRIC_TYPE = "issues"

    async def test_issues(self):
        """Test that the issues are returned."""
        issues_json = dict(total=1, issues=[self.issue()])
        response = await self.get_response(issues_json)
        self.assert_measurement(response, value="1", entities=[self.entity()])
