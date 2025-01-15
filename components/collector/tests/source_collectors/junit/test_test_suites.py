"""Unit tests for the JUnit XML test suites collector."""

from .base import JUnitCollectorTestCase


class JUnitTestSuitesTest(JUnitCollectorTestCase):
    """Unit tests for the JUnit XML test suites collector."""

    METRIC_TYPE = "test_suites"

    def setUp(self):
        """Extend to set up JUnit test data."""
        super().setUp()
        self.expected_entities = [
            self.create_entity("ts1", "errored", passed=1, errored=1, failed=1, skipped=1),
            self.create_entity("ts2", "errored", errored=1),
            self.create_entity("ts3", "failed", failed=1),
            self.create_entity("ts4", "skipped", skipped=1),
            self.create_entity("ts5", "passed", passed=1),
        ]

    def create_entity(  # noqa: PLR0913
        self,
        name: str,
        result: str,
        passed: int = 0,
        errored: int = 0,
        failed: int = 0,
        skipped: int = 0,
    ) -> dict[str, str]:
        """Create a JUnit measurement entity."""
        return {
            "key": name,
            "suite_name": name,
            "suite_result": result,
            "tests": str(passed + errored + failed + skipped),
            "passed": str(passed),
            "errored": str(errored),
            "failed": str(failed),
            "skipped": str(skipped),
        }

    async def test_test_suites(self):
        """Test that the number of test suites is returned."""
        response = await self.collect(get_request_text=self.JUNIT_XML)
        self.assert_measurement(response, value="5", total="5", entities=self.expected_entities)

    async def test_failed_suites(self):
        """Test that the failed suites are returned."""
        self.set_source_parameter("test_result", ["failed"])
        response = await self.collect(get_request_text=self.JUNIT_XML)
        expected_entities = [entity for entity in self.expected_entities if entity["suite_result"] == "failed"]
        self.assert_measurement(response, value="1", total="5", entities=expected_entities)

    async def test_empty_test_suites(self):
        """Test that a JUnit XML file with an empty testsuites node works."""
        response = await self.collect(get_request_text=self.JUNIT_XML_EMPTY_TEST_SUITES)
        self.assert_measurement(response, value="0", total="0")

    async def test_one_top_level_test_suite(self):
        """Test that a JUnit XML file with one top level test suite works."""
        xml = """
        <testsuite name="ts1" timestamp="2009-12-19T17:58:59" failures="0" errors="1" skipped="0" tests="1">
            <testcase name="tc1" classname="cn"><error/></testcase>
        </testsuite>
        """
        response = await self.collect(get_request_text=xml)
        expected_entities = [self.create_entity("ts1", "errored", errored=1)]
        self.assert_measurement(response, value="1", total="1", entities=expected_entities)

    async def test_one_top_level_nested_test_suite(self):
        """Test that a JUnit XML file with one top level nested test suite works."""
        xml = """
        <testsuite name="ts1" timestamp="2009-12-19T17:58:59" failures="0" errors="1" skipped="0" tests="1">
            <testsuite name="ts1-1" timestamp="2009-12-19T17:58:59" failures="0" errors="1" skipped="0" tests="1">
                <testcase name="tc1" classname="cn"><error/></testcase>
            </testsuite>
        </testsuite>
        """
        response = await self.collect(get_request_text=xml)
        expected_entities = [self.create_entity("ts1-1", "errored", errored=1)]
        self.assert_measurement(response, value="1", total="1", entities=expected_entities)
