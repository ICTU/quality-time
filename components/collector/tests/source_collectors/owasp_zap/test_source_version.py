"""Unit tests for the OWASP ZAP source version collector."""

from .base import OWASPZAPTestCase


class OWASPZAPSourceVersionTest(OWASPZAPTestCase):
    """Unit tests for the OWASP ZAP source version collector."""

    METRIC_TYPE = "source_version"

    async def test_source_version(self):
        """Test that the source version is returned."""
        xml = """<?xml version="1.0"?><OWASPZAPReport version="2.7.0"></OWASPZAPReport>"""
        response = await self.collect(get_request_text=xml)
        self.assert_measurement(response, value="2.7.0")

    async def test_source_version_zap_weekly(self):
        """Test that the source version is returned."""
        xml = """<?xml version="1.0"?><OWASPZAPReport version="D-2022-01-01"></OWASPZAPReport>"""
        response = await self.collect(get_request_text=xml)
        self.assert_measurement(response, value="2022.1.1")
