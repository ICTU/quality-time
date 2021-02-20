"""Unit tests for the JUnit XML test report source up-to-dateness collector."""

from datetime import datetime

from .base import JUnitCollectorTestCase


class JUnitSourceUpToDatenessTest(JUnitCollectorTestCase):
    """Unit tests for the source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        response = await self.collect(get_request_text=self.JUNIT_XML)
        expected_age = (datetime.now() - datetime(2009, 12, 19, 17, 58, 59)).days
        self.assert_measurement(response, value=str(expected_age))
