"""Unit tests for the OWASP ZAP time passed collector."""

from datetime import datetime

from .base import OWASPZAPTestCase


class OWASPZAPTimePassedTest(OWASPZAPTestCase):
    """Unit tests for the OWASP ZAP tine passed collector."""

    METRIC_TYPE = "time_passed"

    async def test_time_passed(self):
        """Test that the source age in days is returned."""
        xml = """<?xml version="1.0"?><OWASPZAPReport generated="Thu, 28 Mar 2019 13:20:20"></OWASPZAPReport>"""
        response = await self.collect(get_request_text=xml)
        expected_age = (datetime.now() - datetime(2019, 3, 28, 13, 20, 20)).days
        self.assert_measurement(response, value=str(expected_age))
