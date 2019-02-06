"""Unit tests for the SonarQube source."""

import unittest
from unittest.mock import Mock, patch

from collector.collector import Collector


class SonarQubeTest(unittest.TestCase):
    """Unit tests for the SonarQube metrics."""

    def setUp(self):
        """Test fixture."""
        Collector.RESPONSE_CACHE.clear()

    def test_version(self):
        """Test that the SonarQube version is returned."""
        mock_response = Mock()
        mock_response.text = "2.2.1"
        sources = dict(a=dict(type="sonarqube", url="http://sonar"))
        with patch("requests.get", return_value=mock_response):
            response = Collector().get("version", sources)
        self.assertEqual("2.2.1", response["sources"][0]["measurement"])

    def test_violations(self):
        """Test that the number of violations is returned."""
        mock_response = Mock()
        mock_response.json.return_value = dict(total="10")
        sources = dict(a=dict(type="sonarqube", url="http://sonar", component="id"))
        with patch("requests.get", return_value=mock_response):
            response = Collector().get("violations", sources)
        self.assertEqual("10", response["sources"][0]["measurement"])

    def test_tests(self):
        """Test that the number of tests is returned."""
        mock_response = Mock()
        mock_response.json.return_value = dict(component=dict(measures=[dict(metric="tests", value="88")]))
        sources = dict(a=dict(type="sonarqube", url="http://sonar", component="id"))
        with patch("requests.get", return_value=mock_response):
            response = Collector().get("tests", sources)
        self.assertEqual("88", response["sources"][0]["measurement"])

    def test_covered_lines(self):
        """Test that the number of covered lines is returned."""
        mock_response = Mock()
        mock_response.json.return_value = dict(
            component=dict(
                measures=[dict(metric="lines_to_cover", value="100"), dict(metric="uncovered_lines", value="10")]))
        sources = dict(a=dict(type="sonarqube", url="http://sonar", component="id"))
        with patch("requests.get", return_value=mock_response):
            response = Collector().get("covered_lines", sources)
        self.assertEqual("90", response["sources"][0]["measurement"])

    def test_covered_branches(self):
        """Test that the number of covered branches is returned."""
        mock_response = Mock()
        mock_response.json.return_value = dict(
            component=dict(
                measures=[
                    dict(metric="conditions_to_cover", value="100"), dict(metric="uncovered_conditions", value="10")]))
        sources = dict(a=dict(type="sonarqube", url="http://sonar", component="id"))
        with patch("requests.get", return_value=mock_response):
            response = Collector().get("covered_branches", sources)
        self.assertEqual("90", response["sources"][0]["measurement"])
