"""Unit tests for the Jira issue status collector."""

from .base import JiraTestCase


class JiraIssuesTest(JiraTestCase):
    """Unit tests for the Jira issue status collector."""

    METRIC_TYPE = "issue_status"

    def setUp(self):
        """Extend to add an issue tracker to the metric."""
        super().setUp()
        self.metric["issue_tracker"] = dict(type="jira", parameters=dict(url="https://jira"))
        self.metric["issue_ids"] = ["FOO-42"]

    def assert_issue_status(self, response, summary: str = None, connection_error: str = None, parse_error: str = None):
        """Assert that the issue has the expected attributes."""
        issue_status = response.as_dict()["issue_status"][0]
        self.assertEqual("FOO-42", issue_status["issue_id"])
        if summary:
            self.assertEqual(summary, issue_status["summary"])
        if connection_error or parse_error:
            self.assertNotIn("name", issue_status)
            if connection_error:
                self.assertIn(connection_error, issue_status["connection_error"])
                self.assertNotIn("parse_error", issue_status)
            if parse_error:
                self.assertIn(parse_error, issue_status["parse_error"])
                self.assertNotIn("connection_error", issue_status)
        else:
            self.assertEqual("Issue name", issue_status["name"])
            self.assertEqual("1970-01-01T00:00:00.000+0000", issue_status["created"])
            self.assertNotIn("connection_error", issue_status)
            self.assertNotIn("parse_error", issue_status)
        self.assertEqual(
            "https://jira/rest/api/2/issue/FOO-42?fields=created,status,summary,updated", issue_status["api_url"]
        )
        self.assertEqual("https://jira/browse/FOO-42", issue_status["landing_url"])

    async def test_issue_status(self):
        """Test that the issue status is returned."""
        issue_status_json = dict(fields=dict(status=dict(name="Issue name"), created="1970-01-01T00:00:00.000+0000"))
        response = await self.collect(get_request_json_return_value=issue_status_json)
        self.assert_issue_status(response)

    async def test_issue_summary(self):
        """Test that the issue summary is returned."""
        issue_status_json = dict(
            fields=dict(status=dict(name="Issue name"), summary="Issue summary", created="1970-01-01T00:00:00.000+0000")
        )
        response = await self.collect(get_request_json_return_value=issue_status_json)
        self.assert_issue_status(response, summary="Issue summary")

    async def test_connection_error(self):
        """Test that the issue status is returned, even when there is a connection error."""
        response = await self.collect(get_request_side_effect=BrokenPipeError)
        self.assert_issue_status(response, connection_error="BrokenPipeError")

    async def test_parse_error(self):
        """Test that the issue status is returned, even when there is a parse error."""
        issue_status_json = dict(fields=dict(status=None))
        response = await self.collect(get_request_json_return_value=issue_status_json)
        self.assert_issue_status(response, parse_error="TypeError")
