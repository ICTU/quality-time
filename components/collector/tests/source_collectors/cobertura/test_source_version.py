"""Unit tests for the Cobertura source version collector."""

from .base import CoberturaTestCase


class CoberturaSourceVersionTest(CoberturaTestCase):
    """Unit tests for the Cobertura source version collector."""

    COBERTURA_XML = '<coverage version="2.1.3" />'
    METRIC_TYPE = "source_version"
    METRIC_ADDITION = "min"

    async def test_source_version(self):
        """Test that the source version is returned."""
        response = await self.collect(get_request_text=self.COBERTURA_XML)
        self.assert_measurement(response, value="2.1.3")

    async def test_zipped_report(self):
        """Test that a zipped report can be read."""
        self.set_source_parameter("url", "https://cobertura.zip")
        response = await self.collect(get_request_content=self.zipped_report(("cobertura.xml", self.COBERTURA_XML)))
        self.assert_measurement(response, value="2.1.3")
