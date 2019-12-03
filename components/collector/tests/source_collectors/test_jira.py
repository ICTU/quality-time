"""Unit tests for the Jira metric source."""

from datetime import datetime, timedelta

from dateutil.parser import parse

from collector_utilities.functions import days_ago
from .source_collector_test_case import SourceCollectorTestCase


class JiraTestCase(SourceCollectorTestCase):
    """Base class for Jira unit tests."""

    def setUp(self):
        super().setUp()
        self.sources = dict(
            source_id=dict(
                type="jira",
                parameters=dict(
                    url="https://jira/", jql="query", story_points_field="field",
                    manual_test_execution_frequency_field="desired_test_frequency",
                    manual_test_duration_field="field")))
        self.fields_json = []


class JiraIssuesTest(JiraTestCase):
    """Unit tests for the Jira issue collector."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="issues", addition="sum", sources=self.sources)

    def test_nr_of_issues(self):
        """Test that the number of issues is returned."""
        issues_json = dict(total=42)
        response = self.collect(self.metric, get_request_json_side_effect=[self.fields_json, issues_json])
        self.assert_measurement(response, value="42")

    def test_issues(self):
        """Test that the issues are returned."""
        issues_json = dict(total=1, issues=[dict(key="key", id="id", fields=dict(summary="Summary"))])
        response = self.collect(self.metric, get_request_json_side_effect=[self.fields_json, issues_json])
        self.assert_measurement(response, entities=[dict(key="id", summary="Summary", url="https://jira/browse/key")])


class JiraManualTestExecutionTest(JiraTestCase):
    """Unit tests for the Jira manual test execution collector."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="manual_test_execution", addition="sum", sources=self.sources)

    def test_nr_of_test_cases(self):
        """Test that the number of test cases is returned."""
        test_cases_json = dict(
            issues=[
                dict(key="key1", id="id1",
                     fields=dict(
                         comment=dict(
                             comments=[dict(updated="2019-10-02T11:07:02.444+0200")]), summary="Tested too long ago")),
                dict(key="key2", id="id2", fields=dict(comment=dict(comments=[]), summary="Never tested")),
                dict(key="key3", id="id3",
                     fields=dict(
                         comment=dict(comments=[dict(updated=str(datetime.now()))]), summary="Recently tested")),
                dict(key="key4", id="id4",
                     fields=dict(
                         comment=dict(comments=[dict(updated=str(datetime.now()-timedelta(days=10)))]),
                         desired_test_frequency="5",
                         summary="Tested too long ago according to its own desired frequency"))])
        response = self.collect(
            self.metric, get_request_json_side_effect=[self.fields_json, test_cases_json])
        expected_days = str(days_ago(parse("2019-10-02T11:07:02.444+0200")))
        self.assert_measurement(
            response, value="2",
            entities=[
                dict(key="id1", summary="Tested too long ago", url="https://jira/browse/key1",
                     days_untested=expected_days, desired_test_frequency="21"),
                dict(key="id4", summary="Tested too long ago according to its own desired frequency",
                     url="https://jira/browse/key4", days_untested="10", desired_test_frequency="5")])

    def test_nr_of_test_cases_with_field_name(self):
        """Test that the number of test cases is returned when the field name for the test frequency is specified
        by name."""
        fields_json = [dict(name="Required test frequency", id="custom_field_001")]
        self.sources["source_id"]["parameters"]["manual_test_execution_frequency_field"] = "Required test frequency"
        test_cases_json = dict(
            issues=[
                dict(key="key", id="id",
                     fields=dict(
                         comment=dict(comments=[dict(updated=str(datetime.now()-timedelta(days=10)))]),
                         custom_field_001="5", summary="Tested too long ago according to its own desired frequency"))])
        response = self.collect(
            self.metric, get_request_json_side_effect=[fields_json, test_cases_json])
        self.assert_measurement(
            response, value="1",
            entities=[
                dict(key="id", summary="Tested too long ago according to its own desired frequency",
                     url="https://jira/browse/key", days_untested="10", desired_test_frequency="5")])


class JiraReadyUserStoryPointsTest(JiraTestCase):
    """Unit tests for the Jira ready story points collector."""

    def test_nr_story_points(self):
        """Test that the number of story points is returned."""
        metric = dict(type="ready_user_story_points", addition="sum", sources=self.sources)
        user_stories_json = dict(
            issues=[
                dict(key="1", id="1", fields=dict(summary="summary 1", field=10)),
                dict(key="2", id="2", fields=dict(summary="summary 2", field=32))])
        response = self.collect(
            metric, get_request_json_side_effect=[self.fields_json, user_stories_json])
        self.assert_measurement(
            response, value="42",
            entities=[
                dict(key="1", summary="summary 1", url="https://jira/browse/1", points=10.0),
                dict(key="2", summary="summary 2", url="https://jira/browse/2", points=32.0)])


class JiraManualTestDurationTest(JiraTestCase):
    """Unit tests for the Jira manual test duration collector."""

    def test_duration(self):
        """Test that the duration is returned."""
        metric = dict(type="manual_test_duration", addition="sum", sources=self.sources)
        test_cases_json = dict(
            issues=[
                dict(key="1", id="1", fields=dict(summary="summary 1", field=10)),
                dict(key="2", id="2", fields=dict(summary="summary 2", field=15)),
                dict(key="3", id="3", fields=dict(summary="summary 3", field=None))])
        response = self.collect(
            metric, get_request_json_side_effect=[self.fields_json, test_cases_json])
        self.assert_measurement(
            response, value="25",
            entities=[
                dict(duration=10.0, key="1", summary="summary 1", url="https://jira/browse/1"),
                dict(duration=15.0, key="2", summary="summary 2", url="https://jira/browse/2")])
