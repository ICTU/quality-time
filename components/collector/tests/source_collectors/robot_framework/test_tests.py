"""Unit tests for the Robot Framework tests collector."""

from .base import RobotFrameworkTestCase


class RobotFrameworkTestReportTest(RobotFrameworkTestCase):
    """Unit tests for the Robot Framework XML tests collector."""

    METRIC_TYPE = "tests"
    LANDING_URL = "https://robot_framework"

    def robot_entity(self, *, key: str, name: str, result: str, suite: str) -> dict[str, str]:
        """Create a Robot Framework entity."""
        return {
            "key": key,
            "test_name": name,
            "test_result": result,
            "suite_name": suite,
            "suite_names": suite,
        }

    async def test_tests(self):
        """Test that the number of tests is returned."""
        expected_entities = [
            self.robot_entity(key="s1-t1", name="Test 1", result="fail", suite="Suite 1"),
            self.robot_entity(key="s1-t2", name="Test 2", result="pass", suite="Suite 1"),
            self.robot_entity(key="s2-t1", name="Test 3", result="pass", suite="Suite 2"),
            self.robot_entity(key="s3-t1", name="Test 4", result="skip", suite="Suite 3"),
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
        expected_entities = [self.robot_entity(key="s1-t1", name="Test 1", result="fail", suite="Suite 1")]
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
        expected_entities = [self.robot_entity(key="s3-t1", name="Test 4", result="skip", suite="Suite 3")]
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
