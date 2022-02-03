"""Unit tests for the Cobertura time passed collector."""

from datetime import datetime

from .base import CoberturaTestCase


class CoberturaTimePassedTest(CoberturaTestCase):
    """Unit tests for the Cobertura time passed collector."""

    COBERTURA_XML = '<coverage timestamp="1553821197442" />'
    METRIC_TYPE = "time_passed"
    METRIC_ADDITION = "max"

    def setUp(self):
        """Extend to compute the expected age of the Cobertura report."""
        super().setUp()
        self.expected_age = str((datetime.utcnow() - datetime.utcfromtimestamp(1553821197.442)).days)

    async def test_time_passed(self):
        """Test that the source age in days is returned."""
        response = await self.collect(get_request_text=self.COBERTURA_XML)
        self.assert_measurement(response, value=self.expected_age)

    async def test_zipped_report(self):
        """Test that a zipped report can be read."""
        self.set_source_parameter("url", "https://example.org/cobertura.zip")
        response = await self.collect(get_request_content=self.zipped_report(("cobertura.xml", self.COBERTURA_XML)))
        self.assert_measurement(response, value=self.expected_age)
