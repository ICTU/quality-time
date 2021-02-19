"""Unit tests for the OWASP Dependency Check source up-to-dateness collector."""

from datetime import datetime, timedelta, timezone

from .base import OWASPDependencyCheckTestCase


class OWASPDependencyCheckTest(OWASPDependencyCheckTestCase):
    """Unit tests for the OWASP Dependency Check source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        xml = """<?xml version="1.0"?>
        <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.2.0.xsd">
            <projectInfo>
                <reportDate>2018-10-03T13:01:24.784+0200</reportDate>
            </projectInfo>
        </analysis>"""
        response = await self.collect(self.metric, get_request_text=xml)
        timezone_info = timezone(timedelta(hours=2))
        expected_age = (datetime.now(timezone_info) - datetime(2018, 10, 3, 13, 1, 24, 784, tzinfo=timezone_info)).days
        self.assert_measurement(response, value=str(expected_age))
