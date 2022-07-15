"""Unit tests for the Jira issue status collector."""

from model.issue_status import IssueStatusCategory

from .base import JiraTestCase


class JiraIssuesTest(JiraTestCase):
    """Unit tests for the Jira issue status collector."""

    METRIC_TYPE = "issue_status"
    ISSUE_NAME = "Issue name"
    CREATED = "1970-01-01T00:00:00.000+0000"
    RELEASE_NAME = "1.0"
    RELEASE_RELEASED = False
    RELEASE_DATE = "3000-01-02"
    SPRINT_NAME = "Sprint 1"
    SPRINT_STATE = "active"
    SPRINT_ENDDATE = "3000-01-01"

    def setUp(self):
        """Extend to add an issue tracker to the metric."""
        super().setUp()
        self.metric["issue_tracker"] = dict(type="jira", parameters=dict(url="https://jira"))
        self.metric["issue_ids"] = ["FOO-42"]

    def assert_issue_status(  # pylint: disable=too-many-arguments
        self,
        response,
        summary: str = None,
        connection_error: str = None,
        parse_error: str = None,
        status_category: IssueStatusCategory = "todo",
        release: bool = False,
        sprint: bool = False,
    ) -> None:
        """Assert that the issue has the expected attributes."""
        issue_status = response.as_dict()["issue_status"][0]
        self.assertEqual("FOO-42", issue_status["issue_id"])
        if summary:
            self.assertEqual(summary, issue_status["summary"])
        if connection_error or parse_error:
            self.assertNotIn("name", issue_status)
            self.assertNotIn("status_category", issue_status)
            if connection_error:
                self.assertIn(connection_error, issue_status["connection_error"])
                self.assertNotIn("parse_error", issue_status)
            if parse_error:
                self.assertIn(parse_error, issue_status["parse_error"])
                self.assertNotIn("connection_error", issue_status)
        else:
            self.assertEqual(self.ISSUE_NAME, issue_status["name"])
            self.assertEqual(status_category, issue_status["status_category"])
            self.assertEqual(self.CREATED, issue_status["created"])
            if sprint:
                self.assertEqual(self.SPRINT_NAME, issue_status["sprint_name"])
                self.assertEqual(self.SPRINT_STATE, issue_status["sprint_state"])
                self.assertEqual(self.SPRINT_ENDDATE, issue_status["sprint_enddate"])
            else:
                self.assertNotIn("sprint_name", issue_status)
                self.assertNotIn("sprint_state", issue_status)
                self.assertNotIn("sprint_enddate", issue_status)
            if release:
                self.assertEqual(self.RELEASE_NAME, issue_status["release_name"])
                self.assertEqual(self.RELEASE_RELEASED, issue_status["release_released"])
                self.assertEqual(self.RELEASE_DATE, issue_status["release_date"])
            else:
                self.assertNotIn("release_name", issue_status)
                self.assertNotIn("release_released", issue_status)
                self.assertNotIn("release_date", issue_status)
            self.assertNotIn("connection_error", issue_status)
            self.assertNotIn("parse_error", issue_status)
        self.assertEqual(
            "https://jira/rest/agile/1.0/issue/FOO-42?fields=created,status,summary,updated,duedate,fixVersions,sprint",
            issue_status["api_url"],
        )
        self.assertEqual("https://jira/browse/FOO-42", issue_status["landing_url"])

    async def test_issue_status(self):
        """Test that the issue status is returned."""
        issue_status_json = dict(
            fields=dict(status=dict(name=self.ISSUE_NAME, statusCategory=dict(key="new")), created=self.CREATED)
        )
        response = await self.collect(get_request_json_return_value=issue_status_json)
        self.assert_issue_status(response)

    async def test_issue_status_doing(self):
        """Test that the issue status is returned."""
        issue_status_json = dict(
            fields=dict(
                status=dict(name=self.ISSUE_NAME, statusCategory=dict(key="indeterminate")), created=self.CREATED
            )
        )
        response = await self.collect(get_request_json_return_value=issue_status_json)
        self.assert_issue_status(response, status_category="doing")

    async def test_issue_status_done(self):
        """Test that the issue status is returned."""
        issue_status_json = dict(
            fields=dict(status=dict(name=self.ISSUE_NAME, statusCategory=dict(key="done")), created=self.CREATED)
        )
        response = await self.collect(get_request_json_return_value=issue_status_json)
        self.assert_issue_status(response, status_category="done")

    async def test_issue_summary(self):
        """Test that the issue summary is returned."""
        issue_status_json = dict(
            fields=dict(
                status=dict(name=self.ISSUE_NAME, statusCategory=dict(key="new")),
                summary="Issue summary",
                created=self.CREATED,
            )
        )
        response = await self.collect(get_request_json_return_value=issue_status_json)
        self.assert_issue_status(response, summary="Issue summary")

    async def test_issue_release(self):
        """Test that the issue release is returned."""
        issue_status_json = dict(
            fields=dict(
                created=self.CREATED,
                status=dict(name=self.ISSUE_NAME, statusCategory=dict(key="done")),
                fixVersions=[
                    dict(name=self.RELEASE_NAME, released=self.RELEASE_RELEASED, releaseDate=self.RELEASE_DATE)
                ],
            )
        )
        response = await self.collect(get_request_json_return_value=issue_status_json)
        self.assert_issue_status(response, status_category="done", release=True)

    async def test_issue_sprint(self):
        """Test that the issue sprint is returned."""
        issue_status_json = dict(
            fields=dict(
                created=self.CREATED,
                status=dict(name=self.ISSUE_NAME, statusCategory=dict(key="done")),
                sprint=dict(name=self.SPRINT_NAME, state=self.SPRINT_STATE, endDate=self.SPRINT_ENDDATE),
            )
        )
        response = await self.collect(get_request_json_return_value=issue_status_json)
        self.assert_issue_status(response, status_category="done", sprint=True)

    async def test_connection_error(self):
        """Test that the issue status is returned, even when there is a connection error."""
        response = await self.collect(get_request_side_effect=BrokenPipeError)
        self.assert_issue_status(response, connection_error="BrokenPipeError")

    async def test_parse_error(self):
        """Test that the issue status is returned, even when there is a parse error."""
        issue_status_json = dict(fields=dict(status=None))
        response = await self.collect(get_request_json_return_value=issue_status_json)
        self.assert_issue_status(response, parse_error="TypeError")
