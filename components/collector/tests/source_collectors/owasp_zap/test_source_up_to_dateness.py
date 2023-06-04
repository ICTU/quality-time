"""Unit tests for the OWASP ZAP source up-to-dateness collector."""

from collector_utilities.date_time import datetime_fromparts, days_ago

from .base import OWASPZAPTestCase


class OWASPZAPTest(OWASPZAPTestCase):
    """Unit tests for the OWASP ZAP up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        xml = """<?xml version="1.0"?><OWASPZAPReport generated="Thu, 28 Mar 2019 13:20:20"></OWASPZAPReport>"""
        response = await self.collect(get_request_text=xml)
        expected_age = days_ago(datetime_fromparts(2019, 3, 28, 13, 20, 20))
        self.assert_measurement(response, value=str(expected_age))
