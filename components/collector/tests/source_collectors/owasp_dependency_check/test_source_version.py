"""Unit tests for the OWASP Dependency Check source version collector."""

from .base import OWASPDependencyCheckTestCase


class OWASPDependencyCheckVersionTest(OWASPDependencyCheckTestCase):
    """Unit tests for the OWASP Dependency Check source up-to-dateness collector."""

    METRIC_TYPE = "source_version"

    async def test_version(self):
        """Test that the source version is returned."""
        response = await self.collect(get_request_text=self.xml)
        self.assert_measurement(response, value=str("5.2.1"))
