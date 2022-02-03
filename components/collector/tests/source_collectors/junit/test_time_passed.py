"""Unit tests for the JUnit XML test report time passed collector."""

from datetime import datetime

from .base import JUnitCollectorTestCase


class JUnitTimePassedTest(JUnitCollectorTestCase):
    """Unit tests for the JUnit time passed collector."""

    METRIC_TYPE = "time_passed"
    METRIC_ADDITION = "max"

    async def test_time_passed(self):
        """Test that the source age in days is returned."""
        response = await self.collect(get_request_text=self.JUNIT_XML)
        expected_age = (datetime.now() - datetime(2009, 12, 19, 17, 58, 59)).days
        self.assert_measurement(response, value=str(expected_age))

    async def test_empty_test_suites(self):
        """Test that a JUnit XML file with an empty testsuites node works."""
        response = await self.collect(get_request_text=self.JUNIT_XML_EMPTY_TEST_SUITES)
        self.assert_measurement(response, value="0")
