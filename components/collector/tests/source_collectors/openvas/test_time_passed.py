"""Unit tests for the OpenVAS time passed collector."""

from datetime import datetime, timezone

from .base import OpenVASTestCase


class OpenVASTimePassedTest(OpenVASTestCase):
    """Unit tests for the OpenVAS time passed collector."""

    METRIC_TYPE = "time_passed"
    OPENVAS_XML = """
        <report extension="xml" type="scan" content_type="text/xml">
            <name>2019-04-09T17:56:14Z</name>
            <creation_time>2019-04-09T17:56:14Z</creation_time>
            <modification_time>2019-04-09T18:05:40Z</modification_time>
        </report>"""

    async def test_time_passed(self):
        """Test that the report age in days is returned."""
        response = await self.collect(get_request_text=self.OPENVAS_XML)
        expected_age = (datetime.now(timezone.utc) - datetime(2019, 4, 9, 17, 56, 14, tzinfo=timezone.utc)).days
        self.assert_measurement(response, value=str(expected_age))
