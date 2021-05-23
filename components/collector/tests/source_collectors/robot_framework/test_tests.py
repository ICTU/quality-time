"""Unit tests for the Robot Framework tests collector."""

from .base import RobotFrameworkTestCase


class RobotFrameworkTestReportTest(RobotFrameworkTestCase):
    """Unit tests for the Robot Framework XML test report metrics."""

    METRIC_TYPE = "tests"
    LANDING_URL = "https://robot_framework"

    async def test_tests(self):
        """Test that the number of tests is returned."""
        for xml in self.ROBOT_FRAMEWORK_XML_V3, self.ROBOT_FRAMEWORK_XML_V4:
            with self.subTest(xml=xml):
                response = await self.collect(get_request_text=xml)
                expected_entities = [
                    dict(key="s1-t1", name="Test 1", test_result="fail"),
                    dict(key="s1-t2", name="Test 2", test_result="pass"),
                ]
                self.assert_measurement(
                    response, value="2", total="2", entities=expected_entities, landing_url=self.LANDING_URL
                )

    async def test_failed_tests(self):
        """Test that the number of failed tests is returned."""
        for xml in self.ROBOT_FRAMEWORK_XML_V3, self.ROBOT_FRAMEWORK_XML_V4:
            with self.subTest(xml=xml):
                self.set_source_parameter("test_result", ["fail"])
                response = await self.collect(get_request_text=self.ROBOT_FRAMEWORK_XML_V3)
                expected_entities = [dict(key="s1-t1", name="Test 1", test_result="fail")]
                self.assert_measurement(
                    response, value="1", total="2", entities=expected_entities, landing_url=self.LANDING_URL
                )

    async def test_skipped_tests(self):
        """Test that the number of skipped tests is returned."""
        self.set_source_parameter("test_result", ["skip"])
        response = await self.collect(get_request_text=self.ROBOT_FRAMEWORK_XML_V4_WITH_SKIPPED_TESTS)
        expected_entities = [dict(key="s1-t3", name="Test 3", test_result="skip")]
        self.assert_measurement(
            response, value="1", total="3", entities=expected_entities, landing_url=self.LANDING_URL
        )
