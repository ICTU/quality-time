"""Unit tests for the OWASP Dependency-Check JSON source version collector."""

from .base import OWASPDependencyCheckJSONTestCase


class OWASPDependencyCheckJSONVersionTest(OWASPDependencyCheckJSONTestCase):
    """Unit tests for the OWASP Dependency-Check JSON source version collector."""

    METRIC_TYPE = "source_version"

    async def test_version(self):
        """Test that the source version is returned."""
        response = await self.collect(get_request_json_return_value=self.json)
        self.assert_measurement(response, value="6.5.3")
