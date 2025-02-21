"""Unit tests for the JUnit XML tests collector."""

from .base import JUnitCollectorTestCase


class JUnitTestsTest(JUnitCollectorTestCase):
    """Unit tests for the JUnit XML tests collector."""

    METRIC_TYPE = "tests"

    def setUp(self):
        """Extend to set up JUnit test data."""
        super().setUp()
        self.expected_entities = [
            {
                "key": "cn:h1:tc1",
                "old_key": "cn:tc1",
                "name": "tc1",
                "class_name": "cn",
                "host_name": "h1",
                "test_result": "passed",
            },
            {
                "key": "cn:h1:tc2",
                "old_key": "cn:tc2",
                "name": "tc2",
                "class_name": "cn",
                "host_name": "h1",
                "test_result": "failed",
            },
            {
                "key": "cn:h2:tc3",
                "old_key": "cn:tc3",
                "name": "tc3",
                "class_name": "cn",
                "host_name": "h2",
                "test_result": "errored",
            },
            {
                "key": "cn:h2:tc4",
                "old_key": "cn:tc4",
                "name": "tc4",
                "class_name": "cn",
                "host_name": "h2",
                "test_result": "skipped",
            },
            {
                "key": "cn::tc5",
                "old_key": "cn:tc5",
                "name": "tc5",
                "class_name": "cn",
                "host_name": "",
                "test_result": "errored",
            },
            {
                "key": "cn::tc6",
                "old_key": "cn:tc6",
                "name": "tc6",
                "class_name": "cn",
                "host_name": "",
                "test_result": "failed",
            },
            {
                "key": "cn::tc7",
                "old_key": "cn:tc7",
                "name": "tc7",
                "class_name": "cn",
                "host_name": "",
                "test_result": "skipped",
            },
            {
                "key": "cn::tc8",
                "old_key": "cn:tc8",
                "name": "tc8",
                "class_name": "cn",
                "host_name": "",
                "test_result": "passed",
            },
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
                {
                    "key": "cn:h1:tc2",
                    "old_key": "cn:tc2",
                    "name": "tc2",
                    "class_name": "cn",
                    "host_name": "h1",
                    "test_result": "failed",
                },
                {
                    "key": "cn::tc6",
                    "old_key": "cn:tc6",
                    "name": "tc6",
                    "class_name": "cn",
                    "host_name": "",
                    "test_result": "failed",
                },
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

    async def test_repeated_test_case_names_and_class_name(self):
        """Test that repeated test case and class names are distinguished."""
        junit_xml_repeated_test_case_name_and_class_name = """<testsuites>
        <testsuite timestamp="2009-12-19T17:58:59">
            <testcase name="tc1" classname="cn1" hostname="host1"/>
            <testcase name="tc1" classname="cn1" hostname="host2"/>
            <testcase name="tc1" classname="cn2" hostname="host1"/>
            <testcase name="tc1" classname="cn2" hostname="host2"/>
        </testsuite></testsuites>"""
        response = await self.collect(get_request_text=junit_xml_repeated_test_case_name_and_class_name)
        self.assert_measurement(response, value="4", total="4")

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
        self.assert_measurement(
            response,
            value="1",
            total="1",
            entities=[
                {
                    "key": "cn::tc1",
                    "old_key": "cn:tc1",
                    "name": "tc1",
                    "class_name": "cn",
                    "host_name": "",
                    "test_result": "errored",
                },
            ],
        )
