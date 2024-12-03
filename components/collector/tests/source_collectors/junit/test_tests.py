"""Unit tests for the JUnit XML tests collector."""

from .base import JUnitCollectorTestCase


class JUnitTestsTest(JUnitCollectorTestCase):
    """Unit tests for the JUnit XML tests collector."""

    METRIC_TYPE = "tests"

    def setUp(self):
        """Extend to set up JUnit test data."""
        super().setUp()
        self.expected_entities = [
            {"key": "cn:tc1", "old_key": "tc1", "name": "tc1", "class_name": "cn", "test_result": "passed"},
            {"key": "cn:tc2", "old_key": "tc2", "name": "tc2", "class_name": "cn", "test_result": "failed"},
            {"key": "cn:tc3", "old_key": "tc3", "name": "tc3", "class_name": "cn", "test_result": "errored"},
            {"key": "cn:tc4", "old_key": "tc4", "name": "tc4", "class_name": "cn", "test_result": "skipped"},
            {"key": "cn:tc5", "old_key": "tc5", "name": "tc5", "class_name": "cn", "test_result": "errored"},
            {"key": "cn:tc6", "old_key": "tc6", "name": "tc6", "class_name": "cn", "test_result": "failed"},
            {"key": "cn:tc7", "old_key": "tc7", "name": "tc7", "class_name": "cn", "test_result": "skipped"},
            {"key": "cn:tc8", "old_key": "tc8", "name": "tc8", "class_name": "cn", "test_result": "passed"},
        ]

    async def test_tests(self):
        """Test that the number of tests is returned."""
        response = await self.collect(get_request_text=self.JUNIT_XML)
        self.assert_measurement(response, value="8", total="8", entities=self.expected_entities)

    async def test_failed_tests(self):
        """Test that the failed tests are returned."""
        self.set_source_parameter("test_result", ["failed"])
        response = await self.collect(get_request_text=self.JUNIT_XML)
        self.assert_measurement(
            response,
            value="2",
            total="8",
            entities=[
                {"key": "cn:tc2", "old_key": "tc2", "name": "tc2", "class_name": "cn", "test_result": "failed"},
                {"key": "cn:tc6", "old_key": "tc6", "name": "tc6", "class_name": "cn", "test_result": "failed"},
            ],
        )

    async def test_zipped_junit_report(self):
        """Test that the number of tests is returned from a zip with JUnit reports."""
        self.set_source_parameter("url", "junit.zip")
        response = await self.collect(get_request_content=self.zipped_report(("junit.xml", self.JUNIT_XML)))
        self.assert_measurement(response, value="8", total="8", entities=self.expected_entities)

    async def test_empty_test_suites(self):
        """Test that a JUnit XML file with an empty testsuites node works."""
        response = await self.collect(get_request_text=self.JUNIT_XML_EMPTY_TEST_SUITES)
        self.assert_measurement(response, value="0", total="0")

    async def test_repeated_test_case_names(self):
        """Test that repeated test case names are distinguished."""
        junit_xml_repeated_test_case_name = """<testsuites>
        <testsuite timestamp="2009-12-19T17:58:59">
            <testcase name="tc1" classname="cn1"/>
            <testcase name="tc2" classname="cn1"/>
            <testcase name="tc1" classname="cn2"/>
            <testcase name="tc2" classname="cn2"/>
        </testsuite></testsuites>"""
        response = await self.collect(get_request_text=junit_xml_repeated_test_case_name)
        self.assert_measurement(response, value="4", total="4")
