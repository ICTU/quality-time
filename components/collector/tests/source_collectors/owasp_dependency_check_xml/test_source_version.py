"""Unit tests for the OWASP Dependency-Check XML source version collector."""

from .base import OWASPDependencyCheckXMLTestCase


class OWASPDependencyCheckXMLVersionTest(OWASPDependencyCheckXMLTestCase):
    """Unit tests for the OWASP Dependency-Check XML source version collector."""

    METRIC_TYPE = "source_version"

    async def test_version(self):
        """Test that the source version is returned."""
        response = await self.collect(get_request_text=self.xml, get_request_json_return_value={})
        self.assert_measurement(response, value="5.2.1")

    async def test_newer_version(self):
        """Test that the source version is returned, and a message that a newer version is available."""
        response = await self.collect(get_request_text=self.xml, get_request_json_return_value={"tag_name": "6.5.4"})
        self.assert_measurement(response, value="5.2.1", info_message="Latest available version is 6.5.4")
