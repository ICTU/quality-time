"""Unit tests for the SonarQube source."""

from datetime import datetime, timedelta, timezone
import unittest
from unittest.mock import Mock, patch

from src.collector import collect_measurement
from src.collectors.sonarqube import SonarQubeViolations


class SonarQubeTest(unittest.TestCase):
    """Unit tests for the SonarQube metrics."""

    def setUp(self):
        """Test fixture."""
        self.mock_response = Mock()
        self.sources = dict(a=dict(type="sonarqube", parameters=dict(url="http://sonar", component="id")))

    def test_violations_api_url(self):
        """Test that the api url is correct."""
        self.assertEqual(
            "http://sonar/api/issues/search?componentKeys=None&resolved=false&ps=500",
            SonarQubeViolations().api_url(url="http://sonar"))

    def test_blocker_violations_api_url(self):
        """Test that the api url is correct."""
        self.assertEqual(
            "http://sonar/api/issues/search?componentKeys=None&resolved=false&ps=500&severities=BLOCKER",
            SonarQubeViolations().api_url(url="http://sonar", severities=["blocker"]))

    def test_code_smell_violations_api_url(self):
        """Test that the api url is correct."""
        self.assertEqual(
            "http://sonar/api/issues/search?componentKeys=None&resolved=false&ps=500&types=CODE_SMELL",
            SonarQubeViolations().api_url(url="http://sonar", types=["code_smell"]))

    def test_violations(self):
        """Test that the number of violations is returned."""
        self.mock_response.json.return_value = dict(
            total="2",
            issues=[
                dict(key="a", message="a", component="a", severity="INFO", type="BUG"),
                dict(key="b", message="b", component="b", severity="MAJOR", type="CODE_SMELL")])
        metric = dict(type="violations", sources=self.sources)
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(metric)
        self.assertEqual(
            [
                dict(component="a", key="a", message="a", severity="info", type="bug",
                     url="http://sonar/project/issues?id=id&issues=a&open=a"),
                dict(component="b", key="b", message="b", severity="major", type="code_smell",
                     url="http://sonar/project/issues?id=id&issues=b&open=b")
            ],
            response["sources"][0]["units"])
        self.assertEqual("2", response["sources"][0]["value"])

    def test_tests(self):
        """Test that the number of tests is returned."""
        self.mock_response.json.return_value = dict(
            component=dict(measures=[dict(metric="tests", value="88")]))
        metric = dict(type="tests", sources=self.sources)
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(metric)
        self.assertEqual("88", response["sources"][0]["value"])

    def test_uncovered_lines(self):
        """Test that the number of uncovered lines is returned."""
        self.mock_response.json.return_value = dict(
            component=dict(measures=[dict(metric="uncovered_lines", value="10")]))
        metric = dict(type="uncovered_lines", sources=self.sources)
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(metric)
        self.assertEqual("10", response["sources"][0]["value"])

    def test_uncovered_branches(self):
        """Test that the number of uncovered branches is returned."""
        self.mock_response.json.return_value = dict(
            component=dict(measures=[dict(metric="uncovered_conditions", value="10")]))
        metric = dict(type="uncovered_branches", sources=self.sources)
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(metric)
        self.assertEqual("10", response["sources"][0]["value"])

    def test_long_units(self):
        """Test that the number of long units is returned."""
        self.sources["a"]["parameters"]["rules"] = ["rule1"]
        self.mock_response.json.return_value = dict(total="2", issues=[])
        metric = dict(type="long_units", sources=self.sources)
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(metric)
        self.assertEqual("2", response["sources"][0]["value"])

    def test_source_freshness(self):
        """Test that the number of days since the last analysis is returned."""
        self.mock_response.json.return_value = dict(analyses=[dict(date="2019-03-29T14:20:15+0100")])
        metric = dict(type="source_freshness", sources=self.sources)
        tzinfo = timezone(timedelta(hours=1))
        age = (datetime.now(tzinfo) - datetime(2019, 3, 29, 14, 20, 15, tzinfo=tzinfo)).days
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(metric)
        self.assertEqual(str(age), response["sources"][0]["value"])
