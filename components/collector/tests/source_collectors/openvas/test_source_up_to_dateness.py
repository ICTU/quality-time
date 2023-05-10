"""Unit tests for the OpenVAS source up-to-dateness collector."""

from datetime import datetime, UTC

from collector_utilities.date_time import days_ago

from .base import OpenVASTestCase


class OpenVASSourceUpToDatenessTest(OpenVASTestCase):
    """Unit tests for the OpenVAS source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"
    OPENVAS_XML = """
        <report extension="xml" type="scan" content_type="text/xml">
            <name>2019-04-09T17:56:14Z</name>
            <creation_time>2019-04-09T17:56:14Z</creation_time>
            <modification_time>2019-04-09T18:05:40Z</modification_time>
        </report>"""

    async def test_source_up_to_dateness(self):
        """Test that the report age in days is returned."""
        response = await self.collect(get_request_text=self.OPENVAS_XML)
        expected_age = days_ago(datetime(2019, 4, 9, 17, 56, 14, tzinfo=UTC))
        self.assert_measurement(response, value=str(expected_age))
