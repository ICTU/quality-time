"""Unit tests for the Robot Framework tests collector."""

from .base import RobotFrameworkTestCase


class RobotFrameworkTestReportTest(RobotFrameworkTestCase):
    """Unit tests for the Robot Framework XML tests collector."""

    METRIC_TYPE = "tests"
    LANDING_URL = "https://robot_framework"

    async def test_tests(self):
        """Test that the number of tests is returned."""
        expected_entities = [
            {"key": "s1-t1", "test_name": "Test 1", "test_result": "fail", "suite_name": "Suite 1"},
            {"key": "s1-t2", "test_name": "Test 2", "test_result": "pass", "suite_name": "Suite 1"},
            {"key": "s2-t1", "test_name": "Test 3", "test_result": "pass", "suite_name": "Suite 2"},
            {"key": "s3-t1", "test_name": "Test 4", "test_result": "skip", "suite_name": "Suite 3"},
        ]
        for xml in self.ROBOT_FRAMEWORK_XMLS:
            with self.subTest(xml=xml):
                response = await self.collect(get_request_text=xml)
                self.assert_measurement(
                    response,
                    value="4",
                    total="4",
                    entities=expected_entities,
                    landing_url=self.LANDING_URL,
                )

    async def test_failed_tests(self):
        """Test that the number of failed tests is returned."""
        self.set_source_parameter("test_result", ["fail"])
        expected_entities = [{"key": "s1-t1", "test_name": "Test 1", "test_result": "fail", "suite_name": "Suite 1"}]
        for xml in self.ROBOT_FRAMEWORK_XMLS:
            with self.subTest(xml=xml):
                response = await self.collect(get_request_text=xml)
                self.assert_measurement(
                    response,
                    value="1",
                    total="4",
                    entities=expected_entities,
                    landing_url=self.LANDING_URL,
                )

    async def test_skipped_tests(self):
        """Test that the number of skipped tests is returned."""
        self.set_source_parameter("test_result", ["skip"])
        expected_entities = [{"key": "s3-t1", "test_name": "Test 4", "test_result": "skip", "suite_name": "Suite 3"}]
        for xml in self.ROBOT_FRAMEWORK_XMLS:
            with self.subTest(xml=xml):
                response = await self.collect(get_request_text=xml)
                self.assert_measurement(
                    response,
                    value="1",
                    total="4",
                    entities=expected_entities,
                    landing_url=self.LANDING_URL,
                )
