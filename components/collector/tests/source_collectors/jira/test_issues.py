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
        previous_max_results = JiraIssues.max_results
        JiraIssues.max_results = 1
        issues_json1 = dict(total=2, issues=[self.issue()])
        issues_json2 = dict(total=2, issues=[self.issue(key="2")])
        issues_json3 = dict(total=2, issues=[])
        response = await self.collect(
            get_request_json_side_effect=[[], issues_json1, issues_json2, issues_json3, issues_json1, issues_json2]
        )
        JiraIssues.max_results = previous_max_results
        self.assert_measurement(response, value="2", entities=[self.entity(), self.entity(key="2")])

    async def test_token_header(self):
        """Test that the private token is added to the headers."""
        self.set_source_parameter("private_token", "xxx")
        issues_json = dict(total=1, issues=[self.issue()])
        response = await self.get_response(issues_json)
        self.assert_measurement(response, value="1", entities=[self.entity()])

    async def test_determine_max_results_from_api(self):
        """Test that the maxResults param is determined via API call value."""
        issues_json = dict(total=1, issues=[self.issue()])
        response, get_mock, _ = await self.collect(
            get_request_json_side_effect=[[dict(id="field", name="Field")], 50, issues_json, issues_json],
            return_mocks=True
        )
        self.assert_measurement(response, value="1", entities=[self.entity()])
        self.assertIn("&maxResults=50&", get_mock.mock_calls[2].args[0])

    async def test_determine_max_results_from_default(self):
        """Test that the maxResults param is determined through fallback."""
        issues_json = dict(total=1, issues=[self.issue()])
        result, get_mock, _ = await self.collect(
            get_request_json_side_effect=[[dict(id="field", name="Field")], "error", issues_json, issues_json],
            return_mocks=True
        )
        self.assert_measurement(result, value="1", entities=[self.entity()])
        self.assertIn(f"&maxResults={JiraIssues.DEFAULT_MAX_RESULTS}&", get_mock.mock_calls[2].args[0])
