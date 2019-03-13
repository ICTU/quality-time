"""Unit tests for the Jenkins test report source."""

import unittest
from unittest.mock import Mock, patch

from collector.collector import Collector, collect_measurement


class JenkinsTestReportTest(unittest.TestCase):
    """Unit tests for the Jenkins test report metrics."""

    def setUp(self):
        """Test fixture."""
        Collector.RESPONSE_CACHE.clear()

    def test_nr_of_tests(self):
        """Test that the number of tests is returned."""
        mock_response = Mock()
        mock_response.json = Mock(return_value=dict(passCount=4, failCount=2))
        metric = dict(
            type="tests",
            sources=dict(a=dict(type="jenkins_test_report", parameters=dict(url="http://jenkins/job/job"))))
        with patch("requests.get", return_value=mock_response):
            response = collect_measurement(metric)
        self.assertEqual("6", response["sources"][0]["value"])

    def test_nr_of_failed_tests(self):
        """Test that the number of failed tests is returned."""
        mock_response = Mock()
        mock_response.json = Mock(return_value=dict(
            failCount=2, suites=[dict(
                cases=[dict(status="FAILED", name="tc1", className="c1"),
                       dict(status="FAILED", name="tc2", className="c2")])]))
        metric = dict(
            type="failed_tests",
            sources=dict(a=dict(type="jenkins_test_report", parameters=dict(url="http://jenkins/job/job"))))
        with patch("requests.get", return_value=mock_response):
            response = collect_measurement(metric)
        self.assertEqual("2", response["sources"][0]["value"])
        self.assertEqual(
            [dict(class_name="c1", key="tc1", name="tc1", failure_type="failed"),
             dict(class_name="c2", key="tc2", name="tc2", failure_type="failed")],
            response["sources"][0]["units"])
