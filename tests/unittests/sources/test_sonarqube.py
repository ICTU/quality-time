"""Unit tests for the SonarQube source."""

import unittest
from unittest.mock import Mock, patch

import bottle

from quality_time.sources import (SonarQubeCoveredBranches, SonarQubeCoveredLines, SonarQubeTests, SonarQubeVersion, 
                                  SonarQubeViolations)


class SonarQubeTest(unittest.TestCase):
    """Unit tests for the SonarQube metrics."""

    def test_version(self):
        """Test that the SonarQube version is returned."""
        mock_response = Mock()
        mock_response.text = "2.2.1"
        request = bottle.Request(dict(QUERY_STRING="http://localhost/version/sonarqube&url=http://sonar"))
        with patch("requests.get", return_value=mock_response):
            response = SonarQubeVersion(request).get()
        self.assertEqual("2.2.1", response["source_responses"][0]["measurement"])

    def test_violations(self):
        """Test that the number of violations is returned."""
        mock_response = Mock()
        mock_response.json.return_value = dict(total="10")
        request = bottle.Request(
            dict(QUERY_STRING="http://localhost/violations/sonarqube&url=http://sonar&component=id"))
        with patch("requests.get", return_value=mock_response):
            response = SonarQubeViolations(request).get()
        self.assertEqual("10", response["source_responses"][0]["measurement"])

    def test_tests(self):
        """Test that the number of tests is returned."""
        mock_response = Mock()
        mock_response.json.return_value = dict(component=dict(measures=[dict(metric="tests", value="88")]))
        request = bottle.Request(
            dict(QUERY_STRING="http://localhost/tests/sonarqube&url=http://sonar&component=id"))
        with patch("requests.get", return_value=mock_response):
            response = SonarQubeTests(request).get()
        self.assertEqual("88", response["source_responses"][0]["measurement"])

    def test_covered_lines(self):
        """Test that the number of covered lines is returned."""
        mock_response = Mock()
        mock_response.json.return_value = dict(
            component=dict(
                measures=[dict(metric="lines_to_cover", value="100"), dict(metric="uncovered_lines", value="10")]))
        request = bottle.Request(
            dict(QUERY_STRING="http://localhost/covered_lines/sonarqube&url=http://sonar&component=id"))
        with patch("requests.get", return_value=mock_response):
            response = SonarQubeCoveredLines(request).get()
        self.assertEqual("90", response["source_responses"][0]["measurement"])
 
    def test_covered_branches(self):
        """Test that the number of covered branches is returned."""
        mock_response = Mock()
        mock_response.json.return_value = dict(
            component=dict(
                measures=[
                    dict(metric="conditions_to_cover", value="100"), dict(metric="uncovered_conditions", value="10")]))
        request = bottle.Request(
            dict(QUERY_STRING="http://localhost/covered_branches/sonarqube&url=http://sonar&component=id"))
        with patch("requests.get", return_value=mock_response):
            response = SonarQubeCoveredBranches(request).get()
        self.assertEqual("90", response["source_responses"][0]["measurement"])
