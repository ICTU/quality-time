"""Unit tests for the Jira metric source."""

from datetime import datetime, timedelta

from dateutil.parser import parse
from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class JiraTestCase(SourceCollectorTestCase):
    """Base class for Jira unit tests."""

    METRIC_TYPE = "Subclass responsibility"

    def setUp(self):
        super().setUp()
        self.url = "https://jira"
        self.sources = dict(
            source_id=dict(
                type="jira",
                parameters=dict(
                    url=self.url, jql="query", story_points_field="field",
                    manual_test_execution_frequency_field="desired_test_frequency",
                    manual_test_duration_field="field", board="Board 2")))
        self.metric = dict(type=self.METRIC_TYPE, addition="sum", sources=self.sources)
        self.created = "2020-08-06T16:36:48.000+0200"

    def issue(self, key="1", **fields):
        """Create a Jira issue."""
        return dict(id=key, key=key, fields=dict(created=self.created, summary=f"Summary {key}", **fields))

    def entity(self, key="1", created=None, updated=None, issuetype="Unknown issue type", **kwargs):
        """Create an entity."""
        return dict(
            key=key, summary=f"Summary {key}", url=f"{self.url}/browse/{key}", created=created or self.created,
            updated=updated, status=None, priority=None, type=issuetype, **kwargs)

    async def get_response(self, issues_json, fields_json=None):
        """Get the collector's response."""
        return await self.collect(self.metric, get_request_json_side_effect=[fields_json or [], issues_json])


class JiraIssuesTest(JiraTestCase):
    """Unit tests for the Jira issue collector."""

    METRIC_TYPE = "issues"

    async def test_issues(self):
        """Test that the issues are returned."""
        issues_json = dict(total=1, issues=[self.issue()])
        response = await self.get_response(issues_json)
        self.assert_measurement(response, value="1", entities=[self.entity()])


class JiraManualTestExecutionTest(JiraTestCase):
    """Unit tests for the Jira manual test execution collector."""

    METRIC_TYPE = "manual_test_execution"

    def setUp(self):
        super().setUp()
        self.ten_days_ago = str(datetime.now() - timedelta(days=10))

    async def test_nr_of_test_cases(self):
        """Test that the number of test cases is returned."""
        long_ago = "2019-10-02T11:07:02.444+0200"
        test_cases_json = dict(
            issues=[
                self.issue(key="1", comment=dict(comments=[dict(updated=long_ago)])),
                self.issue(key="2", comment=dict(comments=[])),
                self.issue(key="3", comment=dict(comments=[dict(updated=str(datetime.now()))])),
                self.issue(
                    key="4", comment=dict(comments=[dict(updated=self.ten_days_ago)]), desired_test_frequency="5")])
        response = await self.get_response(test_cases_json)
        self.assert_measurement(
            response, value="2",
            entities=[
                self.entity(key="1", last_test_date=str(parse(long_ago).date()), desired_test_frequency="21"),
                self.entity(key="4", last_test_date=str(parse(self.ten_days_ago).date()), desired_test_frequency="5")])

    async def test_nr_of_test_cases_with_field_name(self):
        """Test that the number of test cases is returned when the field name for the test frequency is specified
        by name."""
        self.sources["source_id"]["parameters"]["manual_test_execution_frequency_field"] = "Required Test Frequency"
        test_cases_json = dict(
            issues=[self.issue(comment=dict(comments=[dict(updated=self.ten_days_ago)]), custom_field_001="5")])
        fields_json = [dict(name="Required test frequency", id="custom_field_001")]
        response = await self.get_response(test_cases_json, fields_json)
        self.assert_measurement(
            response, value="1",
            entities=[
                self.entity(key="1", last_test_date=str(parse(self.ten_days_ago).date()), desired_test_frequency="5")])


class JiraUserStoryPointsTest(JiraTestCase):
    """Unit tests for the Jira story points collector."""

    METRIC_TYPE = "user_story_points"

    async def test_nr_story_points(self):
        """Test that the number of story points is returned."""
        user_stories_json = dict(issues=[self.issue(key="1", field=10), self.issue(key="2", field=32)])
        response = await self.get_response(user_stories_json)
        self.assert_measurement(
            response, value="42", entities=[self.entity(key="1", points="10.0"), self.entity(key="2", points="32.0")])

    async def test_nr_story_points_with_sprint_field(self):
        """Test that the number of story points and the sprints are returned."""
        user_stories_json = dict(
            issues=[
                self.issue(key="1", field=10, custom_field_001=["...,state=CLOSED,name=Sprint 1,startDate=..."]),
                self.issue(key="2", field=32, custom_field_001=None)])
        fields_json = [dict(name="Sprint", id="custom_field_001")]
        response = await self.get_response(user_stories_json, fields_json)
        self.assert_measurement(
            response, value="42",
            entities=[
                self.entity(key="1", points="10.0", sprint="Sprint 1"), self.entity(key="2", points="32.0", sprint="")])


class JiraManualTestDurationTest(JiraTestCase):
    """Unit tests for the Jira manual test duration collector."""

    METRIC_TYPE = "manual_test_duration"

    async def test_duration(self):
        """Test that the duration is returned."""
        test_cases_json = dict(
            issues=[self.issue(key="1", field=10), self.issue(key="2", field=15), self.issue(key="3", field=None)])
        response = await self.get_response(test_cases_json)
        self.assert_measurement(
            response, value="25",
            entities=[self.entity(key="1", duration="10.0"), self.entity(key="2", duration="15.0")])


class JiraVelocityTest(JiraTestCase):
    """Unit tests for the Jira velocity collector."""

    METRIC_TYPE = "velocity"

    def setUp(self):
        super().setUp()
        base_url = f"{self.url}/secure/RapidBoard.jspa?rapidView=2&view=reporting&chart="
        self.sprint_url = f"{base_url}sprintRetrospective&sprint="
        self.landing_url = f"{base_url}velocityChart"
        self.boards_json1 = dict(
            maxResults=2, startAt=0, isLast=False, values=[dict(id=0, name="Board 0"), dict(id=1, name="Board 1")])
        self.boards_json2 = dict(
            maxResults=2, startAt=2, isLast=True, values=[dict(id=2, name="Board 2"), dict(id=3, name="Board 3")])
        self.velocity_json = dict(
            sprints=[
                dict(id=4, name="Sprint 4", goal="Goal 4"), dict(id=3, name="Sprint 3", goal="Goal 3"),
                dict(id=2, name="Sprint 2", goal="")],
            velocityStatEntries={
                "2": dict(estimated=dict(value=65, text="65.0"), completed=dict(value=30, text="30.0")),
                "3": dict(estimated=dict(value=62, text="62.0"), completed=dict(value=48, text="48.0")),
                "4": dict(estimated=dict(value=40, text="40.0"), completed=dict(value=42, text="42.0"))})

    def sprint_entity(self, key: str, points_completed: float, points_committed: float, goal: bool = True):
        """Create an entity."""
        velocity_type = self.sources["source_id"]["parameters"].get("velocity_type", "completed points")
        points_difference = str(points_completed - points_committed)
        points_measured = {
            "completed points": points_completed, "committed points": points_committed,
            "completed points minus committed points": points_difference}[velocity_type]
        return dict(
            key=key, name=f"Sprint {key}", goal=f"Goal {key}" if goal else "", points_completed=str(points_completed),
            points_committed=str(points_committed), points_difference=str(points_difference),
            points_measured=str(points_measured), url=self.sprint_url + key)

    async def test_completed_velocity(self):
        """Test that the completed velocity is returned."""
        response = await self.collect(
            self.metric, get_request_json_side_effect=[self.boards_json1, self.boards_json2, self.velocity_json])
        self.assert_measurement(
            response, value="40", landing_url=self.landing_url,
            entities=[
                self.sprint_entity(key="4", points_completed=42.0, points_committed=40.0),
                self.sprint_entity(key="3", points_completed=48.0, points_committed=62.0),
                self.sprint_entity(key="2", points_completed=30.0, points_committed=65.0, goal=False)])

    async def test_committed_velocity(self):
        """Test that the committed velocity is returned."""
        self.sources["source_id"]["parameters"]["velocity_type"] = "committed points"
        response = await self.collect(
            self.metric, get_request_json_side_effect=[self.boards_json1, self.boards_json2, self.velocity_json])
        self.assert_measurement(
            response, value="56", landing_url=self.landing_url,
            entities=[
                self.sprint_entity(key="4", points_completed=42.0, points_committed=40.0),
                self.sprint_entity(key="3", points_completed=48.0, points_committed=62.0),
                self.sprint_entity(key="2", points_completed=30.0, points_committed=65.0, goal=False)])

    async def test_velocity_difference(self):
        """Test that the difference between completed and committed velocity is returned."""
        self.sources["source_id"]["parameters"]["velocity_type"] = "completed points minus committed points"
        response = await self.collect(
            self.metric, get_request_json_side_effect=[self.boards_json1, self.boards_json2, self.velocity_json])
        self.assert_measurement(
            response, value="-16", landing_url=self.landing_url,
            entities=[
                self.sprint_entity(key="4", points_completed=42.0, points_committed=40.0),
                self.sprint_entity(key="3", points_completed=48.0, points_committed=62.0),
                self.sprint_entity(key="2", points_completed=30.0, points_committed=65.0, goal=False)])

    async def test_velocity_missing_board(self):
        """Test that no velocity is returned if the board name or id is invalid."""
        boards_json = dict(startAt=0, maxResults=50, isLast=True, values=[dict(id=1, name="Board 1")])
        response = await self.collect(self.metric, get_request_json_side_effect=[boards_json])
        self.assert_measurement(
            response, value=None, connection_error="Could not find a Jira board with id or name", landing_url=self.url)
