"""Unit tests for the JUnit XML test report source."""

import unittest
from unittest.mock import Mock, patch

from collector.collector import Collector, collect_measurement


class JUnitTestReportTest(unittest.TestCase):
    """Unit tests for the JUnit XML test report metrics."""

    def setUp(self):
        """Test fixture."""
        Collector.RESPONSE_CACHE.clear()

    def test_tests(self):
        """Test that the number of tests is returned."""
        mock_response = Mock()
        mock_response.text = """<testsuites><testsuite tests="2"></testsuite></testsuites>"""
        metric = dict(type="tests", sources=dict(a=dict(type="junit", parameters=dict(url="junit.xml"))))
        with patch("requests.get", return_value=mock_response):
            response = collect_measurement(metric)
        self.assertEqual("2", response["sources"][0]["value"])

    def test_failed_tests(self):
        """Test that the number of failed tests is returned."""
        mock_response = Mock()
        mock_response.text = """<testsuites><testsuite failures="3"></testsuite></testsuites>"""
        metric = dict(type="failed_tests", sources=dict(a=dict(type="junit", parameters=dict(url="junit.xml"))))
        with patch("requests.get", return_value=mock_response):
            response = collect_measurement(metric)
        self.assertEqual("3", response["sources"][0]["value"])

    def test_failed_tests_units(self):
        """Test that the failed tests are returned as units."""
        mock_response = Mock()
        mock_response.text = """<testsuites><testsuite failures="1"><testcase name="tc" classname="cn"><failure/>
        </testcase></testsuite></testsuites>"""
        metric = dict(type="failed_tests", sources=dict(a=dict(type="junit", parameters=dict(url="junit.xml"))))
        with patch("requests.get", return_value=mock_response):
            response = collect_measurement(metric)
        self.assertEqual(
            [dict(key="tc", name="tc", class_name="cn", failure_type="failed")],
            response["sources"][0]["units"])
