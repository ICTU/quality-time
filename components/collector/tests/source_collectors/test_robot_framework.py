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
        super().setUp()
        self.metric = dict(type="tests", sources=self.sources, addition="sum")
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

    async def test_tests(self):
        """Test that the number of tests is returned."""
        response = await self.collect(self.metric, get_request_text=self.xml)
        expected_entities = [
            dict(key="s1-t1", name="Test 1", test_result="fail"),
            dict(key="s1-t2", name="Test 2", test_result="pass")]
        self.assert_measurement(response, value="2", entities=expected_entities, landing_url="report.html")

    async def test_failed_tests(self):
        """Test that the number of failed tests is returned."""
        self.sources["source_id"]["parameters"]["test_result"] = ["fail"]
        response = await self.collect(self.metric, get_request_text=self.xml)
        expected_entities = [dict(key="s1-t1", name="Test 1", test_result="fail")]
        self.assert_measurement(response, value="1", entities=expected_entities, landing_url="report.html")


class RobotFrameworkSourceUpToDatenessTest(RobotFrameworkTestCase):
    """Unit test for the source up-to-dateness metric."""

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        xml = """<?xml version="1.0"?><robot generated="2009-12-19T17:58:59"/>"""
        metric = dict(type="source_up_to_dateness", sources=self.sources, addition="max")
        response = await self.collect(metric, get_request_text=xml)
        expected_age = (datetime.now() - datetime(2009, 12, 19, 17, 58, 59)).days
        self.assert_measurement(response, value=str(expected_age))
