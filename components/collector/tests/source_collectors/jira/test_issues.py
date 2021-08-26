"""Unit tests for the Jira issues collector."""

from source_collectors.jira.issues import JiraIssues

from .base import JiraTestCase


class JiraIssuesTest(JiraTestCase):
    """Unit tests for the Jira issue collector."""

    METRIC_TYPE = "issues"

    async def test_issues(self):
        """Test that the issues are returned."""
        issues_json = dict(total=1, issues=[self.issue()])
        response = await self.get_response(issues_json)
        self.assert_measurement(response, value="1", entities=[self.entity()])

    async def test_pagination(self):
        """Test that multiple pages of issues are returned."""
        JiraIssues.MAX_RESULTS = 1
        issues_json1 = dict(total=2, issues=[self.issue()])
        issues_json2 = dict(total=2, issues=[self.issue(key="2")])
        response = await self.collect(get_request_json_side_effect=[[], issues_json1, issues_json2])
        self.assert_measurement(response, value="2", entities=[self.entity(), self.entity(key="2")])
