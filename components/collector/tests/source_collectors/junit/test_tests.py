"""Unit tests for the JUnit XML test report tests collector."""

from .base import JUnitCollectorTestCase


class JUnitTestReportTest(JUnitCollectorTestCase):
    """Unit tests for the JUnit XML test report metrics."""

    METRIC_TYPE = "tests"

    def setUp(self):
        """Extend to set up JUnit test data."""
        super().setUp()
        self.expected_entities = [
            dict(key="tc1", name="tc1", class_name="cn", test_result="passed"),
            dict(key="tc2", name="tc2", class_name="cn", test_result="passed"),
            dict(key="tc3", name="tc3", class_name="cn", test_result="failed"),
            dict(key="tc4", name="tc4", class_name="cn", test_result="errored"),
            dict(key="tc5", name="tc5", class_name="cn", test_result="skipped"),
        ]

    async def test_tests(self):
        """Test that the number of tests is returned."""
        response = await self.collect(get_request_text=self.JUNIT_XML)
        self.assert_measurement(response, value="5", total="5", entities=self.expected_entities)

    async def test_failed_tests(self):
        """Test that the failed tests are returned."""
        self.set_source_parameter("test_result", ["failed"])
        response = await self.collect(get_request_text=self.JUNIT_XML)
        self.assert_measurement(
            response,
            value="1",
            total="5",
            entities=[dict(key="tc3", name="tc3", class_name="cn", test_result="failed")],
        )

    async def test_zipped_junit_report(self):
        """Test that the number of tests is returned from a zip with JUnit reports."""
        self.set_source_parameter("url", "junit.zip")
        response = await self.collect(get_request_content=self.zipped_report(("junit.xml", self.JUNIT_XML)))
        self.assert_measurement(response, value="5", total="5", entities=self.expected_entities)
