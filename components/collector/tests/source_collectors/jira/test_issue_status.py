"""Unit tests for the Jira issue status collector."""

from .base import JiraTestCase


class JiraIssuesTest(JiraTestCase):
    """Unit tests for the Jira issue collector."""

    METRIC_TYPE = "issue_status"

    def setUp(self):
        """Extend to add a issue tracker to the metric."""
        super().setUp()
        self.metric["issue_tracker"] = dict(type="jira", parameters=dict(url="https://jira"))
        self.metric["tracker_issue"] = "FOO-42"

    def assert_issue_status(self, response, connection_error: str = None, parse_error: str = None):
        """Assert that the issue has the expected attributes."""
        issue_status = response.as_dict()["issue_status"]
        self.assertEqual("FOO-42", issue_status["issue"])
        any_error = connection_error or parse_error
        self.assertEqual(None if any_error else "Issue name", issue_status["name"])
        self.assertEqual(None if any_error else "Issue description", issue_status["description"])
        self.assertEqual("https://jira/rest/api/2/issue/FOO-42?fields=status", issue_status["api_url"])
        self.assertEqual("https://jira/browse/FOO-42", issue_status["landing_url"])
        if connection_error:
            self.assertIn(connection_error, issue_status["connection_error"])
        else:
            self.assertEqual(None, issue_status["connection_error"])
        if parse_error:
            self.assertIn(parse_error, issue_status["parse_error"])
        else:
            self.assertEqual(None, issue_status["parse_error"])

    async def test_issue_status(self):
        """Test that the issue status is returned."""
        issue_status_json = dict(fields=dict(status=dict(name="Issue name", description="Issue description")))
        response = await self.collect(get_request_json_return_value=issue_status_json)
        self.assert_issue_status(response)

    async def test_connection_error(self):
        """Test that the issue status is returned, even when there is a connection error."""
        response = await self.collect(get_request_side_effect=BrokenPipeError)
        self.assert_issue_status(response, connection_error="BrokenPipeError")

    async def test_parse_error(self):
        """Test that the issue status is returned, even when there is a parse error."""
        issue_status_json = dict(fields=dict(status=None))
        response = await self.collect(get_request_json_return_value=issue_status_json)
        self.assert_issue_status(response, parse_error="TypeError")
