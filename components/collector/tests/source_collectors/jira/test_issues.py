"""Unit tests for the Jira issues collector."""

import aiohttp

from source_collectors.jira.issues import JiraIssues

from .base import JiraTestCase


class JiraIssuesTest(JiraTestCase):
    """Unit tests for the Jira issue collector."""

    METRIC_TYPE = "issues"

    async def test_issues(self):
        """Test that the issues are returned."""
        issues_json = {"total": 1, "issues": [self.issue()]}
        response = await self.get_response(issues_json)
        self.assert_measurement(response, value="1", entities=[self.entity()])

    async def test_pagination(self):
        """Test that multiple pages of issues are returned."""
        previous_max_results = JiraIssues.max_results
        JiraIssues.max_results = 1
        issues_json1 = {"total": 2, "issues": [self.issue()]}
        issues_json2 = {"total": 2, "issues": [self.issue(key="2")]}
        issues_json3 = {"total": 2, "issues": []}
        side_effect = [[], self.JIRA_SERVER_INFO, issues_json1, issues_json2, issues_json3, issues_json1, issues_json2]
        response = await self.collect(get_request_json_side_effect=side_effect)
        JiraIssues.max_results = previous_max_results
        self.assert_measurement(response, value="2", entities=[self.entity(), self.entity(key="2")])

    async def test_token_header(self):
        """Test that the private token is added to the headers."""
        self.set_source_parameter("private_token", "xxx")
        issues_json = {"total": 1, "issues": [self.issue()]}
        response = await self.get_response(issues_json)
        self.assert_measurement(response, value="1", entities=[self.entity()])

    async def test_determine_max_results_from_api(self):
        """Test that the maxResults param is determined via API call value."""
        issues_json = {"total": 1, "issues": [self.issue()]}
        side_effect = [[{"id": "field", "name": "Field"}], 51, self.JIRA_SERVER_INFO, issues_json, issues_json]
        response, get_mock, _ = await self.collect(get_request_json_side_effect=side_effect, return_mocks=True)
        self.assert_measurement(response, value="1", entities=[self.entity()])
        self.assertIn("&maxResults=51&", get_mock.mock_calls[3].args[0])

    async def test_determine_max_results_from_default(self):
        """Test that the maxResults param is determined through fallback."""
        issues_json = {"total": 1, "issues": [self.issue()]}
        side_effect = [[{"id": "field", "name": "Field"}], "error", self.JIRA_SERVER_INFO, issues_json, issues_json]
        result, get_mock, _ = await self.collect(get_request_json_side_effect=side_effect, return_mocks=True)
        self.assert_measurement(result, value="1", entities=[self.entity()])
        self.assertIn(f"&maxResults={JiraIssues.DEFAULT_MAX_RESULTS}&", get_mock.mock_calls[3].args[0])

    async def test_api_v2(self):
        """Test that the Jira API version used is v2 by default."""
        issues_json = {"total": 1, "issues": [self.issue()]}
        side_effect = [[{"id": "field", "name": "Field"}], 50, self.JIRA_SERVER_INFO, issues_json, issues_json]
        _, get_mock, _ = await self.collect(get_request_json_side_effect=side_effect, return_mocks=True)
        self.assertTrue(get_mock.mock_calls[2].startswith("https://jira/rest/api/2"))

    async def test_api_v3(self):
        """Test that the Jira API version can be set to v3."""
        self.set_source_parameter("api_version", "v3")
        issues_json = {"total": 1, "issues": [self.issue()]}
        side_effect = [[{"id": "field", "name": "Field"}], 50, self.JIRA_SERVER_INFO, issues_json, issues_json]
        _, get_mock, _ = await self.collect(get_request_json_side_effect=side_effect, return_mocks=True)
        self.assertTrue(get_mock.mock_calls[2].startswith("https://jira/rest/api/3"))

    async def test_deployment_type_cloud(self):
        """Test that the Jira Cloud API is used if the Jira URL points to Jira Cloud."""
        issues_json = {"total": 1, "issues": [self.issue()]}
        side_effect = [[{"id": "field", "name": "Field"}], 50, {"deploymentType": "Cloud"}, issues_json, issues_json]
        _, get_mock, _ = await self.collect(get_request_json_side_effect=side_effect, return_mocks=True)
        self.assertTrue(get_mock.mock_calls[3].startswith("https://jira/rest/api/3/search/jql?jql="))

    async def test_deployment_type_data_center(self):
        """Test that the Jira Data Center API is used if the Jira URL points to Jira Data Center."""
        issues_json = {"total": 1, "issues": [self.issue()]}
        side_effect = [[{"id": "field", "name": "Field"}], 50, self.JIRA_SERVER_INFO, issues_json, issues_json]
        _, get_mock, _ = await self.collect(get_request_json_side_effect=side_effect, return_mocks=True)
        self.assertTrue(get_mock.mock_calls[3].startswith("https://jira/rest/api/3/search?jql="))

    async def test_assume_deployment_type_data_center_on_connection_error(self):
        """Test that the Jira Data Center API is used if the server info results in an error."""
        issues_json = {"total": 1, "issues": [self.issue()]}
        side_effect = [[{"id": "field", "name": "Field"}], 50, aiohttp.ClientError, issues_json, issues_json]
        _, get_mock, _ = await self.collect(get_request_json_side_effect=side_effect, return_mocks=True)
        self.assertTrue(get_mock.mock_calls[3].startswith("https://jira/rest/api/3/search?jql="))

    async def test_assume_deployment_type_data_center_on_parse_error(self):
        """Test that the Jira Data Center API is used if the server info results in an error."""
        issues_json = {"total": 1, "issues": [self.issue()]}
        side_effect = [[{"id": "field", "name": "Field"}], 50, "not a dict", issues_json, issues_json]
        _, get_mock, _ = await self.collect(get_request_json_side_effect=side_effect, return_mocks=True)
        self.assertTrue(get_mock.mock_calls[3].startswith("https://jira/rest/api/3/search?jql="))
