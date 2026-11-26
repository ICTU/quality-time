"""Unit tests for the Jira issue status collector."""

from typing import TYPE_CHECKING, ClassVar

from .base import JiraTestCase

if TYPE_CHECKING:
    from model.issue_status import IssueStatusCategory


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
    STORY_POINTS_FIELDS: ClassVar[list[dict[str, str]]] = [
        {"id": "customfield_10002", "name": "Story Points"},
        {"id": "customfield_10016", "name": "Story point estimate"},
    ]

    def setUp(self):
        """Extend to replace the metric sources with an issue tracker."""
        super().setUp()
        self.metric["sources"] = {}
        self.metric["issue_tracker"] = {"type": "jira", "parameters": {"url": "https://jira"}}
        self.metric["issue_ids"] = ["FOO-42"]

    async def collect_issue_status(self, issue_status_json, fields_json: list | None = None):
        """Collect the issue status, given the Jira fields and issue JSON."""
        return await self.collect_measurement(get_request_json_side_effect=[fields_json or [], issue_status_json])

    def issue_status_json(self, **extra_fields) -> dict:
        """Return the Jira issue JSON, with optional extra fields."""
        status = {"name": self.ISSUE_NAME, "statusCategory": {"key": "new"}}
        return {"fields": {"created": self.CREATED, "status": status, **extra_fields}}

    def assert_issue_status(  # noqa: PLR0913, PLR0917
        self,
        measurement,
        summary: str | None = None,
        connection_error: str | None = None,
        parse_error: str | None = None,
        status_category: IssueStatusCategory = "todo",
        release: bool = False,
        sprint: bool = False,
        story_points: float | None = None,
        story_points_field_id: str = "",
    ) -> None:
        """Assert that the issue has the expected attributes."""
        issue_status = measurement.as_dict()["issue_status"][0]
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
            if story_points is None:
                self.assertNotIn("story_points", issue_status)
            else:
                self.assertEqual(story_points, issue_status["story_points"])
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
            "https://jira/rest/agile/1.0/issue/FOO-42?fields=created,status,summary,updated,duedate,fixVersions,sprint"
            + (f",{story_points_field_id}" if story_points_field_id else ""),
            issue_status["api_url"],
        )
        self.assertEqual("https://jira/browse/FOO-42", issue_status["landing_url"])

    async def test_issue_status(self):
        """Test that the issue status is returned."""
        issue_status_json = {
            "fields": {"status": {"name": self.ISSUE_NAME, "statusCategory": {"key": "new"}}, "created": self.CREATED},
        }
        measurement = await self.collect_issue_status(issue_status_json)
        self.assert_issue_status(measurement)

    async def test_issue_status_doing(self):
        """Test that the issue status is returned."""
        issue_status_json = {
            "fields": {
                "status": {"name": self.ISSUE_NAME, "statusCategory": {"key": "indeterminate"}},
                "created": self.CREATED,
            },
        }
        measurement = await self.collect_issue_status(issue_status_json)
        self.assert_issue_status(measurement, status_category="doing")

    async def test_issue_status_done(self):
        """Test that the issue status is returned."""
        issue_status_json = {
            "fields": {"status": {"name": self.ISSUE_NAME, "statusCategory": {"key": "done"}}, "created": self.CREATED},
        }
        measurement = await self.collect_issue_status(issue_status_json)
        self.assert_issue_status(measurement, status_category="done")

    async def test_issue_summary(self):
        """Test that the issue summary is returned."""
        issue_status_json = {
            "fields": {
                "status": {"name": self.ISSUE_NAME, "statusCategory": {"key": "new"}},
                "summary": "Issue summary",
                "created": self.CREATED,
            },
        }
        measurement = await self.collect_issue_status(issue_status_json)
        self.assert_issue_status(measurement, summary="Issue summary")

    async def test_issue_release(self):
        """Test that the issue release is returned."""
        issue_status_json = {
            "fields": {
                "created": self.CREATED,
                "status": {"name": self.ISSUE_NAME, "statusCategory": {"key": "done"}},
                "fixVersions": [
                    {"name": self.RELEASE_NAME, "released": self.RELEASE_RELEASED, "releaseDate": self.RELEASE_DATE},
                ],
            },
        }
        measurement = await self.collect_issue_status(issue_status_json)
        self.assert_issue_status(measurement, status_category="done", release=True)

    async def test_issue_sprint(self):
        """Test that the issue sprint is returned."""
        issue_status_json = {
            "fields": {
                "created": self.CREATED,
                "status": {"name": self.ISSUE_NAME, "statusCategory": {"key": "done"}},
                "sprint": {"name": self.SPRINT_NAME, "state": self.SPRINT_STATE, "endDate": self.SPRINT_ENDDATE},
            },
        }
        measurement = await self.collect_issue_status(issue_status_json)
        self.assert_issue_status(measurement, status_category="done", sprint=True)

    async def test_issue_story_points(self):
        """Test that the issue story points are returned, using the default story points field."""
        issue_status_json = self.issue_status_json(customfield_10002=5.0)
        measurement = await self.collect_issue_status(issue_status_json, self.STORY_POINTS_FIELDS)
        self.assert_issue_status(measurement, story_points=5.0, story_points_field_id="customfield_10002")

    async def test_issue_story_points_from_configured_field_name(self):
        """Test that the issue story points are returned, using the story points field configured by name."""
        self.metric["issue_tracker"]["parameters"]["story_points_field"] = "Story point estimate"
        issue_status_json = self.issue_status_json(customfield_10002=5.0, customfield_10016=3)
        measurement = await self.collect_issue_status(issue_status_json, self.STORY_POINTS_FIELDS)
        self.assert_issue_status(measurement, story_points=3.0, story_points_field_id="customfield_10016")

    async def test_issue_story_points_from_configured_field_id(self):
        """Test that the issue story points are returned, using the story points field configured by id."""
        self.metric["issue_tracker"]["parameters"]["story_points_field"] = "customfield_10016"
        issue_status_json = self.issue_status_json(customfield_10016=3)
        measurement = await self.collect_issue_status(issue_status_json, self.STORY_POINTS_FIELDS)
        self.assert_issue_status(measurement, story_points=3.0, story_points_field_id="customfield_10016")

    async def test_issue_without_story_points(self):
        """Test that no story points are returned if the issue has none."""
        issue_status_json = self.issue_status_json(customfield_10002=None)
        measurement = await self.collect_issue_status(issue_status_json, self.STORY_POINTS_FIELDS)
        self.assert_issue_status(measurement, story_points_field_id="customfield_10002")

    async def test_missing_story_points_field(self):
        """Test that no story points are returned, and no error is reported, if the story points field doesn't exist."""
        self.metric["issue_tracker"]["parameters"]["story_points_field"] = "Missing field"
        issue_status_json = self.issue_status_json()
        measurement = await self.collect_issue_status(issue_status_json, self.STORY_POINTS_FIELDS)
        self.assert_issue_status(measurement)

    async def test_connection_error(self):
        """Test that the issue status is returned, even when there is a connection error."""
        measurement = await self.collect_measurement(get_request_side_effect=BrokenPipeError)
        self.assert_issue_status(measurement, connection_error="BrokenPipeError")

    async def test_parse_error(self):
        """Test that the issue status is returned, even when there is a parse error."""
        issue_status_json = {"fields": {"status": None}}
        measurement = await self.collect_issue_status(issue_status_json)
        self.assert_issue_status(measurement, parse_error="TypeError")
