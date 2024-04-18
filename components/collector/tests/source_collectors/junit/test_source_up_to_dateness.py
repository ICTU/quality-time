"""Unit tests for the JUnit XML test report source up-to-dateness collector."""

from collector_utilities.date_time import datetime_from_parts, days_ago

from .base import JUnitCollectorTestCase


class JUnitSourceUpToDatenessTest(JUnitCollectorTestCase):
    """Unit tests for the source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        response = await self.collect(get_request_text=self.JUNIT_XML)
        expected_age = days_ago(datetime_from_parts(2009, 12, 19, 17, 58, 59))
        self.assert_measurement(response, value=str(expected_age))

    async def test_empty_test_suites(self):
        """Test that a JUnit XML file with an empty testsuites node works."""
        response = await self.collect(get_request_text=self.JUNIT_XML_EMPTY_TEST_SUITES)
        self.assert_measurement(response, value="0")
