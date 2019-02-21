"""Unit tests for the SonarQube source."""

import unittest
from unittest.mock import Mock, patch

from collector.collector import Collector


class SonarQubeTest(unittest.TestCase):
    """Unit tests for the SonarQube metrics."""

    def setUp(self):
        """Test fixture."""
        Collector.RESPONSE_CACHE.clear()

    def test_violations(self):
        """Test that the number of violations is returned."""
        mock_response = Mock()
        mock_response.json.return_value = dict(
            total="2",
            issues=[
                dict(key="a", message="a", component="a", severity="INFO", type="BUG"),
                dict(key="b", message="b", component="b", severity="MAJOR", type="CODE_SMELL")])
        sources = dict(
            a=dict(type="sonarqube", parameters=dict(url="http://sonar", component="id")))
        with patch("requests.get", return_value=mock_response):
            response = Collector().get("violations", sources)
        self.assertEqual(
            [
                dict(component="a", key="a", message="a", severity="info", type="bug",
                     url="http://sonar/project/issues?id=id&open=a"),
                dict(component="b", key="b", message="b", severity="major", type="code_smell",
                     url="http://sonar/project/issues?id=id&open=b")
            ],
            response["sources"][0]["units"])
        self.assertEqual("2", response["sources"][0]["value"])

    def test_tests(self):
        """Test that the number of tests is returned."""
        mock_response = Mock()
        mock_response.json.return_value = dict(
            component=dict(measures=[dict(metric="tests", value="88")]))
        sources = dict(
            a=dict(type="sonarqube", parameters=dict(url="http://sonar", component="id")))
        with patch("requests.get", return_value=mock_response):
            response = Collector().get("tests", sources)
        self.assertEqual("88", response["sources"][0]["value"])

    def test_covered_lines(self):
        """Test that the number of covered lines is returned."""
        mock_response = Mock()
        mock_response.json.return_value = dict(
            component=dict(
                measures=[dict(metric="lines_to_cover", value="100"), dict(metric="uncovered_lines", value="10")]))
        sources = dict(
            a=dict(type="sonarqube", parameters=dict(url="http://sonar", component="id")))
        with patch("requests.get", return_value=mock_response):
            response = Collector().get("covered_lines", sources)
        self.assertEqual("90", response["sources"][0]["value"])

    def test_covered_branches(self):
        """Test that the number of covered branches is returned."""
        mock_response = Mock()
        mock_response.json.return_value = dict(
            component=dict(
                measures=[
                    dict(metric="conditions_to_cover", value="100"), dict(metric="uncovered_conditions", value="10")]))
        sources = dict(
            a=dict(type="sonarqube", parameters=dict(url="http://sonar", component="id")))
        with patch("requests.get", return_value=mock_response):
            response = Collector().get("covered_branches", sources)
        self.assertEqual("90", response["sources"][0]["value"])
