"""Unit tests for the JUnit XML test report source."""

from datetime import datetime
import unittest
from unittest.mock import Mock, patch

from src.collector import collect_measurement


class JUnitTestReportTest(unittest.TestCase):
    """Unit tests for the JUnit XML test report metrics."""

    def test_tests(self):
        """Test that the number of tests is returned."""
        self.mock_response = Mock()
        metric = dict(
            type="tests", sources=dict(a=dict(type="junit", parameters=dict(url="junit.xml"))), addition="sum")
        self.mock_response.text = """<testsuites><testsuite tests="2"></testsuite></testsuites>"""
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(metric)
        self.assertEqual("2", response["sources"][0]["value"])


class JunitTestReportFailedTestsTest(unittest.TestCase):
    """Unit tests for the failed test metric."""

    def setUp(self):
        self.mock_response = Mock()
        self.metric = dict(
            type="failed_tests", sources=dict(a=dict(type="junit", parameters=dict(url="junit.xml"))), addition="sum")

    def test_failed_tests(self):
        """Test that the number of failed tests is returned."""
        self.mock_response.text = """<testsuites><testsuite failures="3"></testsuite></testsuites>"""
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(self.metric)
        self.assertEqual("3", response["sources"][0]["value"])

    def test_failed_tests_units(self):
        """Test that the failed tests are returned as units."""
        self.mock_response.text = """<testsuites><testsuite failures="1"><testcase name="tc" classname="cn"><failure/>
        </testcase></testsuite></testsuites>"""
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(self.metric)
        self.assertEqual(
            [dict(key="tc", name="tc", class_name="cn", failure_type="failed")],
            response["sources"][0]["units"])


class JUnitSourceFreshnessTest(unittest.TestCase):
    """Unit test for the source freshness metric."""

    def test_source_freshness(self):
        """Test that the source age in days is returned."""
        mock_response = Mock()
        mock_response.text = """<?xml version="1.0"?>
        <testsuite timestamp="2009-12-19T17:58:59">
        </testsuite>"""
        metric = dict(type="source_freshness", sources=dict(a=dict(type="junit", parameters=dict(url="junit.xml"))),
                      addition="max")
        with patch("requests.get", return_value=mock_response):
            response = collect_measurement(metric)
        expected_age = (datetime.utcnow() - datetime(2009, 12, 19, 17, 58, 59)).days
        self.assertEqual(str(expected_age), response["sources"][0]["value"])
