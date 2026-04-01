"""Unit tests for the OWASP Dependency-Check JSON source version collector."""

from .base import OWASPDependencyCheckJSONTestCase


class OWASPDependencyCheckJSONVersionTest(OWASPDependencyCheckJSONTestCase):
    """Unit tests for the OWASP Dependency-Check JSON source version collector."""

    METRIC_TYPE = "source_version"

    async def test_version(self):
        """Test that the source version is returned."""
        response = await self.collect(get_request_json_return_value=self.json)
        self.assert_measurement(response, value="6.5.3")

    async def test_newer_version(self):
        """Test that the source version is returned, and a message that a newer version is available."""
        json = self.json.copy()
        json["tag_name"] = "6.5.4"
        response = await self.collect(get_request_json_return_value=json)
        self.assert_measurement(response, value="6.5.3", info_message="Latest available version is 6.5.4")
