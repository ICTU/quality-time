"""Unit tests for the Jira issues collector."""

import json
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, Mock, patch

import aiohttp

from source_collectors.jira.issues import JiraIssues

from .base import JiraTestCase

if TYPE_CHECKING:
    from model import MetricMeasurement


class JiraIssuesTest(JiraTestCase):
    """Unit tests for the Jira issue collector."""

    METRIC_TYPE = "issues"

    async def test_issues(self):
        """Test that the issues are returned."""
        issues_json = {"total": 1, "issues": [self.issue()]}
        measurement = await self.get_response(issues_json)
        self.assert_measurement(measurement, value="1", entities=[self.entity()])

    async def test_pagination(self):
        """Test that multiple pages of issues are returned."""
        previous_max_results = JiraIssues.max_results
        JiraIssues.max_results = 1
        issues_json1 = {"total": 2, "issues": [self.issue()]}
        issues_json2 = {"total": 2, "issues": [self.issue(key="2")]}
        issues_json3 = {"total": 2, "issues": []}
        side_effect = [[], issues_json1, issues_json2, issues_json3, issues_json1, issues_json2]
        measurement = await self.collect_measurement(get_request_json_side_effect=side_effect)
        JiraIssues.max_results = previous_max_results
        self.assert_measurement(measurement, value="2", entities=[self.entity(), self.entity(key="2")])

    async def test_token_header(self):
        """Test that the private token is added to the headers."""
        self.set_source_parameter("private_token", "xxx")
        issues_json = {"total": 1, "issues": [self.issue()]}
        measurement = await self.get_response(issues_json)
        self.assert_measurement(measurement, value="1", entities=[self.entity()])

    async def test_determine_max_results_from_api(self):
        """Test that the maxResults param is determined via API call value."""
        issues_json = {"total": 1, "issues": [self.issue()]}
        side_effect = [[{"id": "field", "name": "Field"}], 51, issues_json, issues_json]
        measurement, get_mock, _ = await self.collect_measurement_and_mocks(get_request_json_side_effect=side_effect)
        self.assert_measurement(measurement, value="1", entities=[self.entity()])
        self.assertIn("&maxResults=51&", get_mock.mock_calls[2].args[0])

    async def test_determine_max_results_from_default(self):
        """Test that the maxResults param is determined through fallback."""
        issues_json = {"total": 1, "issues": [self.issue()]}
        side_effect = [[{"id": "field", "name": "Field"}], "error", issues_json, issues_json]
        measurement, get_mock, _ = await self.collect_measurement_and_mocks(get_request_json_side_effect=side_effect)
        self.assert_measurement(measurement, value="1", entities=[self.entity()])
        self.assertIn(f"&maxResults={JiraIssues.DEFAULT_MAX_RESULTS}&", get_mock.mock_calls[2].args[0])

    async def test_api_v2(self):
        """Test that the Jira API version used is v2 by default."""
        issues_json = {"total": 1, "issues": [self.issue()]}
        side_effect = [[{"id": "field", "name": "Field"}], 50, issues_json, issues_json]
        _, get_mock, _ = await self.collect_measurement_and_mocks(get_request_json_side_effect=side_effect)
        self.assertTrue(get_mock.mock_calls[2].startswith("https://jira/rest/api/2"))

    async def test_api_v3(self):
        """Test that the Jira API version can be set to v3."""
        self.set_source_parameter("api_version", "v3")
        issues_json = {"total": 1, "issues": [self.issue()]}
        side_effect = [[{"id": "field", "name": "Field"}], 50, issues_json, issues_json]
        _, get_mock, _ = await self.collect_measurement_and_mocks(get_request_json_side_effect=side_effect)
        self.assertTrue(get_mock.mock_calls[2].startswith("https://jira/rest/api/3"))


class JiraIssuesErrorTest(JiraTestCase):
    """Unit tests for the Jira issue collector when Jira responds with an error."""

    METRIC_TYPE = "issues"

    @staticmethod
    def error_response(json=None, json_side_effect=None) -> AsyncMock:
        """Create a Jira error response."""
        response = AsyncMock(ok=False, status=400, reason="Bad Request")
        response.json = AsyncMock(return_value=json, side_effect=json_side_effect)
        error = aiohttp.ClientResponseError(Mock(), (), status=400, message="Bad Request")
        response.raise_for_status = Mock(side_effect=error)
        return response

    async def collect_error(self, error_response: AsyncMock) -> tuple[MetricMeasurement, Mock, Mock]:
        """Collect the measurement, with Jira responding with an error to the search request."""
        fields_response = AsyncMock()
        fields_response.json = AsyncMock(return_value=[{"id": "field", "name": "Field"}])
        with patch.object(JiraIssues, "max_results", 50):
            return await self.collect_measurement_and_mocks(get_request_side_effect=[fields_response, error_response])

    async def test_error_messages(self):
        """Test that the error messages Jira returns are added to the connection error."""
        error_messages = ["The value 'abc' does not exist for the field 'project'."]
        response = self.error_response({"errorMessages": error_messages, "errors": {}})
        measurement, get_mock, _ = await self.collect_error(response)
        self.assert_measurement(
            measurement,
            connection_error="Jira responded with HTTP status 400 (Bad Request): "
            "The value 'abc' does not exist for the field 'project'.",
        )
        self.assertFalse(get_mock.mock_calls[1].kwargs["raise_for_status"])

    async def test_field_errors(self):
        """Test that the field errors Jira returns are added to the connection error."""
        response = self.error_response({"errorMessages": [], "errors": {"jql": "Error in the JQL query."}})
        measurement, _, _ = await self.collect_error(response)
        self.assert_measurement(
            measurement, connection_error="Jira responded with HTTP status 400 (Bad Request): Error in the JQL query."
        )

    async def test_error_without_json(self):
        """Test that the HTTP error is the connection error if the error response contains no JSON."""
        response = self.error_response(json_side_effect=json.JSONDecodeError("Expecting value", "<html>", 0))
        measurement, _, _ = await self.collect_error(response)
        self.assert_measurement(measurement, connection_error="400, message='Bad Request'")

    async def test_error_without_error_messages(self):
        """Test that the HTTP error is the connection error if the error response contains no error messages."""
        for json_body in ({}, {"errorMessages": [], "errors": {}}, ["unexpected"]):
            with self.subTest(json_body=json_body):
                measurement, _, _ = await self.collect_error(self.error_response(json_body))
                self.assert_measurement(measurement, connection_error="400, message='Bad Request'")
