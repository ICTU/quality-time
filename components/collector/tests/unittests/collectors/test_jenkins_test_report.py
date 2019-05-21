"""Unit tests for the Jenkins test report source."""

from datetime import datetime
import unittest
from unittest.mock import Mock, patch

from src.collector import MetricCollector


class JenkinsTestReportTest(unittest.TestCase):
    """Unit tests for the Jenkins test report metrics."""

    def test_nr_of_tests(self):
        """Test that the number of tests is returned."""
        mock_response = Mock()
        mock_response.json = Mock(return_value=dict(passCount=4, failCount=2))
        metric = dict(
            type="tests", addition="sum",
            sources=dict(source_id=dict(type="jenkins_test_report", parameters=dict(url="http://jenkins/jobjob"))))
        with patch("requests.get", return_value=mock_response):
            response = MetricCollector(metric).get()
        self.assertEqual("6", response["sources"][0]["value"])

    def test_nr_of_failed_tests(self):
        """Test that the number of failed tests is returned."""
        mock_response = Mock()
        mock_response.json = Mock(return_value=dict(
            failCount=2, suites=[dict(
                cases=[dict(status="FAILED", name="tc1", className="c1"),
                       dict(status="FAILED", name="tc2", className="c2")])]))
        metric = dict(
            type="failed_tests", addition="sum",
            sources=dict(source_ida=dict(type="jenkins_test_report", parameters=dict(url="http://jenkins/job"))))
        with patch("requests.get", return_value=mock_response):
            response = MetricCollector(metric).get()
        self.assertEqual("2", response["sources"][0]["value"])
        self.assertEqual(
            [dict(class_name="c1", key="tc1", name="tc1", failure_type="failed"),
             dict(class_name="c2", key="tc2", name="tc2", failure_type="failed")],
            response["sources"][0]["entities"])

    def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        mock_response = Mock()
        mock_response.json = Mock(return_value=dict(suites=[dict(timestamp="2019-04-02T08:52:50")]))
        metric = dict(
            type="source_up_to_dateness", addition="max",
            sources=dict(source_ida=dict(type="jenkins_test_report", parameters=dict(url="http://jenkins/job"))))
        with patch("requests.get", return_value=mock_response):
            response = MetricCollector(metric).get()
        expected_age = (datetime.now() - datetime(2019, 4, 2, 8, 52, 50)).days
        self.assertEqual(str(expected_age), response["sources"][0]["value"])
