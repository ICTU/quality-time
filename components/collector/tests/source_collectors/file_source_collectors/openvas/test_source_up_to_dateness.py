"""Unit tests for the OpenVAS source up-to-dateness collector."""

from datetime import datetime, timezone

from .base import OpenVASTestCase


class OpenVASSourceUpToDatenessTest(OpenVASTestCase):
    """Unit tests for the OpenVAS source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    async def test_source_up_to_dateness(self):
        """Test that the report age in days is returned."""
        openvas_xml = """
<report extension="xml" type="scan" content_type="text/xml">
    <name>2019-04-09T17:56:14Z</name>
    <creation_time>2019-04-09T17:56:14Z</creation_time>
    <modification_time>2019-04-09T18:05:40Z</modification_time>
</report>"""
        response = await self.collect(self.metric, get_request_text=openvas_xml)
        expected_age = (datetime.now(timezone.utc) - datetime(2019, 4, 9, 17, 56, 14, tzinfo=timezone.utc)).days
        self.assert_measurement(response, value=str(expected_age))
