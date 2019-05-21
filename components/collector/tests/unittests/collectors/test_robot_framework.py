"""Unit tests for the Robot Framework XML test report source."""

from datetime import datetime
import unittest
from unittest.mock import Mock, patch

from src.collector import MetricCollector


class RobotFrameworkTestReportTest(unittest.TestCase):
    """Unit tests for the Robot Framework XML test report metrics."""

    def test_tests(self):
        """Test that the number of tests is returned."""
        mock_response = Mock()
        metric = dict(
            type="tests",
            sources=dict(a=dict(type="robot_framework", parameters=dict(url="output.xml"))),
            addition="sum")
        mock_response.text = """<?xml version="1.0"?>
<robot>
    <statistics>
        <total>
            <stat pass="8" fail="2">Critical Tests</stat>
            <stat pass="8" fail="3">All Tests</stat>
        </total>
    </statistics>
</robot>"""
        with patch("requests.get", return_value=mock_response):
            response = MetricCollector(metric).get()
        self.assertEqual("11", response["sources"][0]["value"])
        self.assertEqual("report.html", response["sources"][0]["landing_url"])


class RobotFrameworkTestReportFailedTestsTest(unittest.TestCase):
    """Unit tests for the failed test metric."""

    def setUp(self):
        self.mock_response = Mock()
        self.metric = dict(
            type="failed_tests",
            sources=dict(source_id=dict(type="robot_framework", parameters=dict(url="output.xml"))),
            addition="sum")

    def test_failed_tests(self):
        """Test that the number of failed tests is returned."""
        self.mock_response.text = """<?xml version="1.0"?>
<robot>
    <statistics>
        <total>
            <stat pass="8" fail="2">Critical Tests</stat>
            <stat pass="8" fail="3">All Tests</stat>
        </total>
    </statistics>
</robot>"""
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(self.metric).get()
        self.assertEqual("3", response["sources"][0]["value"])

    def test_failed_tests_entities(self):
        """Test that the failed tests are returned as entities."""
        self.mock_response.text = """<?xml version="1.0"?>
<robot>
    <suite>
        <test id="s1-t1" name="Test 1">
            <status status="FAIL"></status>
        </test>
        <test id="s1-t2" name="Test 2">
            <status status="PASS"></status>
        </test>
    </suite>
    <statistics>
        <total>
            <stat pass="1" fail="1">Critical Tests</stat>
            <stat pass="1" fail="1">All Tests</stat>
        </total>
    </statistics>
</robot>"""
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(self.metric).get()
        self.assertEqual(
            [dict(key="s1-t1", name="Test 1", failure_type="fail")],
            response["sources"][0]["entities"])


class RobotFrameworkSourceUpToDatenessTest(unittest.TestCase):
    """Unit test for the source up-to-dateness metric."""

    def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        mock_response = Mock()
        mock_response.text = """<?xml version="1.0"?><robot generated="2009-12-19T17:58:59"/>"""
        metric = dict(
            type="source_up_to_dateness",
            sources=dict(source_id=dict(type="robot_framework", parameters=dict(url="output.xml"))),
            addition="max")
        with patch("requests.get", return_value=mock_response):
            response = MetricCollector(metric).get()
        expected_age = (datetime.now() - datetime(2009, 12, 19, 17, 58, 59)).days
        self.assertEqual(str(expected_age), response["sources"][0]["value"])
