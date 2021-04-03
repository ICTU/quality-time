"""Unit tests for the OpenVAS source version collector."""

from .base import OpenVASTestCase


class OpenVASSourceVersionTest(OpenVASTestCase):
    """Unit tests for the OpenVAS source version collector."""

    METRIC_TYPE = "source_version"
    OPENVAS_XML = """
        <report extension="xml" type="scan" content_type="text/xml">
            <report><omp><version>7.0</version></omp></report>
        </report>"""

    async def test_source_version(self):
        """Test that the OpenVAS version is returned."""
        response = await self.collect(get_request_text=self.OPENVAS_XML)
        self.assert_measurement(response, value="7.0")
