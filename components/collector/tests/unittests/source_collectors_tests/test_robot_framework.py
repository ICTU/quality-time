"""Unit tests for the Robot Framework XML test report source."""

from datetime import datetime

from .source_collector_test_case import SourceCollectorTestCase


class RobotFrameworkTestCase(SourceCollectorTestCase):
    """Base class for testing Robot Framework collectors."""

    def setUp(self) -> None:
        super().setUp()
        self.sources = dict(source_id=dict(type="robot_framework", parameters=dict(url="output.xml")))


class RobotFrameworkTestReportTest(RobotFrameworkTestCase):
    """Unit tests for the Robot Framework XML test report metrics."""

    def setUp(self):
        self.xml = """<?xml version="1.0"?>
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

    def test_tests(self):
        """Test that the number of tests is returned."""
        sources = dict(source_id=dict(type="robot_framework", parameters=dict(url="output.xml")))
        metric = dict(type="tests", sources=sources, addition="sum")
        response = self.collect(metric, get_request_text=self.xml)
        self.assert_value("2", response)
        self.assert_entities(
            [
                dict(key="s1-t1", name="Test 1", test_result="fail"),
                dict(key="s1-t2", name="Test 2", test_result="pass")
            ],
            response)
        self.assert_landing_url("report.html", response)

    def test_failed_tests(self):
        """Test that the number of failed tests is returned."""
        sources = dict(source_id=dict(type="robot_framework", parameters=dict(url="output.xml", test_result=["fail"])))
        metric = dict(type="tests", sources=sources, addition="sum")
        response = self.collect(metric, get_request_text=self.xml)
        self.assert_value("1", response)
        self.assert_entities(
            [
                dict(key="s1-t1", name="Test 1", test_result="fail")
            ],
            response)
        self.assert_landing_url("report.html", response)


class RobotFrameworkTestReportFailedTestsTest(RobotFrameworkTestCase):
    """Unit tests for the failed test metric."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="failed_tests", sources=self.sources, addition="sum")

    def test_failed_tests(self):
        """Test that the number of failed tests is returned."""
        xml = """<?xml version="1.0"?>
<robot>
    <statistics>
        <total>
            <stat pass="8" fail="2">Critical Tests</stat>
            <stat pass="8" fail="3">All Tests</stat>
        </total>
    </statistics>
</robot>"""
        response = self.collect(self.metric, get_request_text=xml)
        self.assert_value("3", response)

    def test_failed_tests_entities(self):
        """Test that the failed tests are returned as entities."""
        xml = """<?xml version="1.0"?>
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
        response = self.collect(self.metric, get_request_text=xml)
        self.assert_entities([dict(key="s1-t1", name="Test 1", failure_type="fail")], response)


class RobotFrameworkSourceUpToDatenessTest(RobotFrameworkTestCase):
    """Unit test for the source up-to-dateness metric."""

    def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        xml = """<?xml version="1.0"?><robot generated="2009-12-19T17:58:59"/>"""
        metric = dict(type="source_up_to_dateness", sources=self.sources, addition="max")
        response = self.collect(metric, get_request_text=xml)
        expected_age = (datetime.now() - datetime(2009, 12, 19, 17, 58, 59)).days
        self.assert_value(str(expected_age), response)
