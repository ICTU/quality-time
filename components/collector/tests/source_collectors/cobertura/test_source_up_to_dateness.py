"""Unit tests for the Cobertura source up-to-dateness collector."""

from datetime import datetime

from .base import CoberturaTestCase


class CoberturaSourceUpToDatenessTest(CoberturaTestCase):
    """Unit tests for the Cobertura source up-to-dateness collector."""

    COBERTURA_XML = '<coverage timestamp="1553821197442" />'
    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    def setUp(self):
        """Extend to compute the expected age of the Cobertura report."""
        super().setUp()
        self.expected_age = str((datetime.utcnow() - datetime.utcfromtimestamp(1553821197.442)).days)

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        response = await self.collect(get_request_text=self.COBERTURA_XML)
        self.assert_measurement(response, value=self.expected_age)

    async def test_zipped_report(self):
        """Test that a zipped report can be read."""
        self.set_source_parameter("url", "https://cobertura.zip")
        response = await self.collect(get_request_content=self.zipped_report(("cobertura.xml", self.COBERTURA_XML)))
        self.assert_measurement(response, value=self.expected_age)
