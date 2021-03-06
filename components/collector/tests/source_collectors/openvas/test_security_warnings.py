"""Unit tests for the OpenVAS security warnings collector."""

from .base import OpenVASTestCase


class OpenVASSecurityWarningsTest(OpenVASTestCase):
    """Unit tests for the OpenVAS security warnings collector."""

    METRIC_TYPE = "security_warnings"
    OPENVAS_XML = """<?xml version="1.0"?>
        <report>
            <results>
                <result id="id">
                    <name>Name</name>
                    <description>Description</description>
                    <threat>Low</threat>
                    <host>1.2.3.4</host>
                    <port>80/tcp</port>
                </result>
            </results>
        </report>"""

    async def test_warnings(self):
        """Test that the number of warnings is returned."""
        response = await self.collect(get_request_text=self.OPENVAS_XML)
        expected_entities = [
            dict(key="id", severity="Low", name="Name", description="Description", host="1.2.3.4", port="80/tcp")
        ]
        self.assert_measurement(response, value="1", entities=expected_entities)
