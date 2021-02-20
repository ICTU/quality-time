"""Unit tests for the Robot Framework tests collector."""

from .base import RobotFrameworkTestCase


class RobotFrameworkTestReportTest(RobotFrameworkTestCase):
    """Unit tests for the Robot Framework XML test report metrics."""

    METRIC_TYPE = "tests"
    ROBOT_FRAMEWORK_XML = """<?xml version="1.0"?>
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
        response = await self.collect(self.metric, get_request_text=self.ROBOT_FRAMEWORK_XML)
        expected_entities = [
            dict(key="s1-t1", name="Test 1", test_result="fail"),
            dict(key="s1-t2", name="Test 2", test_result="pass"),
        ]
        self.assert_measurement(
            response, value="2", total="2", entities=expected_entities, landing_url="https://robot_framework"
        )

    async def test_failed_tests(self):
        """Test that the number of failed tests is returned."""
        self.sources["source_id"]["parameters"]["test_result"] = ["fail"]
        response = await self.collect(self.metric, get_request_text=self.ROBOT_FRAMEWORK_XML)
        expected_entities = [dict(key="s1-t1", name="Test 1", test_result="fail")]
        self.assert_measurement(
            response, value="1", total="2", entities=expected_entities, landing_url="https://robot_framework"
        )
