"""Unit tests for the Gatling source-up-to-dateness collector."""

from datetime import datetime

from dateutil.tz import tzutc

from collector_utilities.date_time import days_ago

from .base import GatlingTestCase


class GatlingSourceUpToDatenessTest(GatlingTestCase):
    """Unit tests for the Gatling source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    async def test_no_transactions(self):
        """Test that the age is 0 if there is no date in the HTML."""
        response = await self.collect(get_request_text="<span/>")
        self.assert_measurement(response, value="0")

    async def test_source_up_to_dateness(self):
        """Test that the test age is returned."""
        response = await self.collect(
            get_request_text="""
            <span class="simulation-information-item">
                <span class="simulation-information-label">Date: </span>
                <span>2025-09-10 11:39:26 GMT</span>
            </span>"""
        )
        expected_age = days_ago(datetime(2025, 9, 10, 11, 39, 26, tzinfo=tzutc()))
        self.assert_measurement(response, value=str(expected_age))
