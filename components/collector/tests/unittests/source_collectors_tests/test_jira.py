"""Unit tests for the Jira metric source."""
import json
import os.path
import pathlib

from typing import Dict
from http.client import HTTPException
from unittest import TestCase
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

import logging
import requests

from source_collectors.jira import JiraBase, JiraManualTestExecution
from .source_collector_test_case import SourceCollectorTestCase


def datetime_days_from_now(days: int) -> str:
    """Return date certain number of days ago in string format."""
    return (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def get_jira_json_for_days(test_frequency1: int, last_tested_days_ago1: int,
                           test_frequency2: int, last_tested_days_ago2: int) -> Dict:
    """Return parametrized jira issues dictionary."""
    jira_json = dict(
        issues=[
            dict(key="1", id="1",
                 fields=dict(summary="summary 1",
                             comment=dict(comments=[dict(updated=datetime_days_from_now(last_tested_days_ago1))]))),
            dict(key="2", id="2",
                 fields=dict(summary="summary 2",
                             comment=dict(comments=[dict(updated=datetime_days_from_now(last_tested_days_ago2))])))]
    )
    if test_frequency1:
        jira_json["issues"][0]["fields"]["freq_field"] = test_frequency1
    if test_frequency2:
        jira_json["issues"][1]["fields"]["freq_field"] = test_frequency2
    return jira_json

class JiraTestCase(SourceCollectorTestCase):
    """Base class for Jira unit tests."""

    def setUp(self):
        super().setUp()
        self.sources = dict(
            source_id=dict(
                type="jira",
                parameters=dict(
                    url="https://jira", jql="query", story_points_field="field",
                    manual_test_execution_frequency_field="freq_field", manual_test_duration_field="field")))

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


@patch.object(JiraBase, '_get_fields')
class JiraManualTestExecutionFrequencyTest(JiraTestCase):
    """Unit tests for the Jira manual test duration collector."""

    def test_execution(self, mock__get_fields):
        """Test that the test issues ready to test are returned, according to given frequency."""
        mock__get_fields.return_value = []
        metric = dict(type="manual_test_execution", addition="count", sources=self.sources)
        jira_json = get_jira_json_for_days(15, 13, 10, 11)
        response = self.collect(metric, get_request_json_return_value=jira_json)
        self.assert_measurement(response, value="1")
        self.assertEqual(response["sources"][0]["entities"],
                         [{'key': '2', 'summary': 'summary 2', 'url': 'https://jira/browse/2'}])

    def test_execution_field_found(self, mock__get_fields):
        """Test that when field id is found, issues are returned according to the given frequency."""
        mock__get_fields.return_value = [{"id": "freq_field", "name": "Unimportant"}]
        metric = dict(type="manual_test_execution", addition="count", sources=self.sources)
        jira_json = get_jira_json_for_days(15, 13, 10, 11)
        response = self.collect(metric, get_request_json_return_value=jira_json)
        self.assert_measurement(response, value="1")
        self.assertEqual(response["sources"][0]["entities"],
                         [{'key': '2', 'summary': 'summary 2', 'url': 'https://jira/browse/2'}])

    def test_execution_field_empty(self, mock__get_fields):
        """Test that when the field id is empty, issues are returned according to the default frequency."""
        mock__get_fields.return_value = [{"id": "freq_field", "name": "Freq. Field"}]
        self.sources["source_id"]["parameters"]["manual_test_execution_frequency_field"] = ""
        metric = dict(type="manual_test_execution", addition="count", sources=self.sources)
        jira_json = get_jira_json_for_days(15, 20, 10, 22)
        response = self.collect(metric, get_request_json_return_value=jira_json)
        self.assert_measurement(response, value="1")
        self.assertEqual(response["sources"][0]["entities"],
                         [{'key': '2', 'summary': 'summary 2', 'url': 'https://jira/browse/2'}])

    def test_execution_frequency_field_not_found(self, mock__get_fields):
        """Test that when the field id is not found, an exception is thrown."""
        mock__get_fields.return_value = [{"id": "wrong!", "name": "Not matching also"}]
        metric = dict(type="manual_test_execution", addition="count", sources=self.sources)
        response = self.collect(metric)
        self.assertTrue(response["sources"][0]["parse_error"].endswith(
            "ValueError: Jira field with id or name freq_field does not exist!\n"))

    def test_execution_default_frequency(self, mock__get_fields):
        """Test that the test cases ready to test, according to default frequency od 21 days, are returned."""
        mock__get_fields.return_value = []
        metric = dict(type="manual_test_execution", addition="count", sources=self.sources)
        jira_json = get_jira_json_for_days(0, 20, 0, 22)

        response = self.collect(metric, get_request_json_return_value=jira_json)

        self.assert_measurement(response, value="1")
        self.assertEqual(response["sources"][0]["entities"],
                         [{'key': '2', 'summary': 'summary 2', 'url': 'https://jira/browse/2'}])


class JiraBaseTestCase(TestCase):
    """Class for unit testing JiraBase class."""

    @classmethod
    def setUpClass(cls) -> None:
        data_model_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__)),
                                       "..", "..", "..", "..", "server", "src", "data", "datamodel.json")
        with open(data_model_path) as json_data_model:
            cls.data_model = json.load(json_data_model)
        cls.sources = dict(
            source_id=dict(
                type="jira",
                parameters=dict(
                    url="https://jira", jql="query", story_points_field="field",
                    manual_test_execution_frequency_field="Freq. Field", manual_test_duration_field="field")))

    @patch.object(requests, 'get')
    def test_get_fields(self, mock_get):
        """Test if the _get_fields function works."""
        jira_json = get_jira_json_for_days(15, 13, 10, 11)
        responses = MagicMock(status_code=200, reason='OK', raise_for_status=MagicMock(), sources=self.sources,
                              json=MagicMock(
                                  side_effect=[[{"id": "freq_field", "name": "Freq. Field"}], jira_json, jira_json]))
        mock_get.return_value = responses
        jira_manual_test_execution_collector = JiraManualTestExecution(self.sources["source_id"], self.data_model)

        jira_manual_test_execution_collector.get_subclass('jira', "manual_test_execution")

        result = jira_manual_test_execution_collector.get()
        self.assertEqual(result["value"], "1")
        self.assertEqual(result["entities"], [{'key': '2', 'summary': 'summary 2', 'url': 'https://jira/browse/2'}])

    @patch.object(logging, 'warning')
    @patch.object(requests, 'get')
    def test_get_fields_http_error(self, mock_get, mock_warning):
        """Test if the _get_fields function delivers error, it will be logged and the default frequency will be used."""
        jira_json = get_jira_json_for_days(15, 20, 10, 22)
        responses = MagicMock(status_code=200, reason='OK', raise_for_status=MagicMock(), sources=self.sources,
                              json=MagicMock(side_effect=[HTTPException(), jira_json, jira_json]))
        mock_get.return_value = responses
        jira_manual_test_execution_collector = JiraManualTestExecution(self.sources["source_id"], self.data_model)

        jira_manual_test_execution_collector.get_subclass('jira', "manual_test_execution")

        result = jira_manual_test_execution_collector.get()
        self.assertEqual(result["value"], "1")
        self.assertEqual(result["entities"], [{'key': '2', 'summary': 'summary 2', 'url': 'https://jira/browse/2'}])
        self.assertEqual(mock_warning.call_args.args[0], "Failed to retrieve %s: %s")
        self.assertEqual(mock_warning.call_args.args[1], 'https://jira/rest/api/2/field')
        self.assertIsInstance(mock_warning.call_args.args[2], HTTPException)
