"""Unit tests for the Robot Framework test suites collector."""

from .base import RobotFrameworkTestCase


class RobotFrameworkTestSuitesTest(RobotFrameworkTestCase):
    """Unit tests for the Robot Framework XML test suites collector."""

    METRIC_TYPE = "test_suites"
    LANDING_URL = "https://robot_framework"

    def create_entity(  # noqa: PLR0913
        self,
        key: str,
        name: str,
        result: str,
        tests: int = 0,
        passed: int = 0,
        errored: int = 0,
        failed: int = 0,
        skipped: int = 0,
    ) -> dict[str, str]:
        """Create a Robot Framework test suite entity."""
        return {
            "key": key,
            "suite_result": result,
            "suite_name": name,
            "suite_documentation": name,
            "tests": str(tests),
            "passed": str(passed),
            "errored": str(errored),
            "failed": str(failed),
            "skipped": str(skipped),
        }

    async def test_suites(self):
        """Test that the number of suites is returned."""
        expected_entities = [
            self.create_entity("s1", "Suite 1", "fail", tests=2, passed=1, failed=1),
            self.create_entity("s2", "Suite 2", "pass", tests=1, passed=1),
            self.create_entity("s3", "Suite 3", "skip", tests=1, skipped=1),
        ]
        for xml in self.ROBOT_FRAMEWORK_XMLS:
            with self.subTest(xml=xml):
                response = await self.collect(get_request_text=xml)
                self.assert_measurement(
                    response,
                    value="3",
                    total="5",
                    entities=expected_entities,
                    landing_url=self.LANDING_URL,
                )

    async def test_failed_suites(self):
        """Test that the number of failed tests is returned."""
        self.set_source_parameter("test_result", ["fail"])
        expected_entities = [self.create_entity("s1", "Suite 1", "fail", tests=2, passed=1, failed=1)]
        for xml in self.ROBOT_FRAMEWORK_XMLS:
            with self.subTest(xml=xml):
                response = await self.collect(get_request_text=xml)
                self.assert_measurement(
                    response,
                    value="1",
                    total="5",
                    entities=expected_entities,
                    landing_url=self.LANDING_URL,
                )

    async def test_skipped_suites(self):
        """Test that the number of skipped suites is returned."""
        self.set_source_parameter("test_result", ["skip"])
        expected_entities = [self.create_entity("s3", "Suite 3", "skip", tests=1, skipped=1)]
        for xml in self.ROBOT_FRAMEWORK_XMLS:
            response = await self.collect(get_request_text=xml)
            self.assert_measurement(
                response,
                value="1",
                total="5",
                entities=expected_entities,
                landing_url=self.LANDING_URL,
            )
