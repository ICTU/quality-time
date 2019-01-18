"""Unit tests for the SonarQube source."""

import unittest
from unittest.mock import Mock, patch

from collector.collector import Collector


class SonarQubeTest(unittest.TestCase):
    """Unit tests for the SonarQube metrics."""

    def setUp(self):
        """Test fixture."""
        Collector.RESPONSE_CACHE.clear()
        self.api_url = "version?source=sonarqube&url=http://sonar&component=id"

    def test_version(self):
        """Test that the SonarQube version is returned."""
        mock_response = Mock()
        mock_response.text = "2.2.1"
        with patch("requests.get", return_value=mock_response):
            response = Collector("version?source=sonarqube&url=http://sonar").get()
        self.assertEqual("2.2.1", response["sources"][0]["measurement"])

    def test_violations(self):
        """Test that the number of violations is returned."""
        mock_response = Mock()
        mock_response.json.return_value = dict(total="10")
        with patch("requests.get", return_value=mock_response):
            response = Collector("violations?source=sonarqube&url=http://sonar&component=id").get()
        self.assertEqual("10", response["sources"][0]["measurement"])

    def test_tests(self):
        """Test that the number of tests is returned."""
        mock_response = Mock()
        mock_response.json.return_value = dict(component=dict(measures=[dict(metric="tests", value="88")]))
        with patch("requests.get", return_value=mock_response):
            response = Collector("tests?source=sonarqube&url=http://sonar&component=id").get()
        self.assertEqual("88", response["sources"][0]["measurement"])

    def test_covered_lines(self):
        """Test that the number of covered lines is returned."""
        mock_response = Mock()
        mock_response.json.return_value = dict(
            component=dict(
                measures=[dict(metric="lines_to_cover", value="100"), dict(metric="uncovered_lines", value="10")]))
        with patch("requests.get", return_value=mock_response):
            response = Collector("covered_lines?source=sonarqube&url=http://sonar&component=id").get()
        self.assertEqual("90", response["sources"][0]["measurement"])

    def test_covered_branches(self):
        """Test that the number of covered branches is returned."""
        mock_response = Mock()
        mock_response.json.return_value = dict(
            component=dict(
                measures=[
                    dict(metric="conditions_to_cover", value="100"), dict(metric="uncovered_conditions", value="10")]))
        with patch("requests.get", return_value=mock_response):
            response = Collector("covered_branches?source=sonarqube&url=http://sonar&component=id").get()
        self.assertEqual("90", response["sources"][0]["measurement"])
