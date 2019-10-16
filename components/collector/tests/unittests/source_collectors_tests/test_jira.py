"""Unit tests for the Jira metric source."""

from .source_collector_test_case import SourceCollectorTestCase


class JiraTestCase(SourceCollectorTestCase):
    """Base class for Jira unit tests."""

    def setUp(self):
        super().setUp()
        self.sources = dict(
            source_id=dict(
                type="jira",
                parameters=dict(
                    url="https://jira", jql="query", story_points_field="field", manual_test_duration_field="field")))


class JiraIssuesTest(JiraTestCase):
    """Unit tests for the Jira issue collector."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="issues", addition="sum", sources=self.sources)

    def test_nr_of_issues(self):
        """Test that the number of issues is returned."""
        response = self.collect(self.metric, get_request_json_return_value=dict(total=42))
        self.assert_measurement(response, value="42")

    def test_issues(self):
        """Test that the issues are returned."""
        jira_json = dict(total=1, issues=[dict(key="key", id="id", fields=dict(summary="Summary"))])
        response = self.collect(self.metric, get_request_json_return_value=jira_json)
        self.assert_measurement(response, entities=[dict(key="id", summary="Summary", url="https://jira/browse/key")])


class JiraReadyUserStoryPointsTest(JiraTestCase):
    """Unit tests for the Jira ready story points collector."""

    def test_nr_story_points(self):
        """Test that the number of story points is returned."""
        metric = dict(type="ready_user_story_points", addition="sum", sources=self.sources)
        jira_json = dict(
            issues=[
                dict(key="1", id="1", fields=dict(summary="summary 1", field=10)),
                dict(key="2", id="2", fields=dict(summary="summary 2", field=32))])
        response = self.collect(metric, get_request_json_return_value=jira_json)
        self.assert_measurement(response, value="42")


class JiraManualTestDurationTest(JiraTestCase):
    """Unit tests for the Jira manual test duration collector."""

    def test_duration(self):
        """Test that the duration is returned."""
        metric = dict(type="manual_test_duration", addition="sum", sources=self.sources)
        jira_json = dict(
            issues=[
                dict(key="1", id="1", fields=dict(summary="summary 1", field=10)),
                dict(key="2", id="2", fields=dict(summary="summary 2", field=15))])
        response = self.collect(metric, get_request_json_return_value=jira_json)
        self.assert_measurement(response, value="25")
