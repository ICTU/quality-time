"""Unit tests for the Gatling performance test duration collector."""

from .base import GatlingTestCase


class GatlingPerformancetestDurationTest(GatlingTestCase):
    """Unit tests for the Gatling performancetest duration collector."""

    METRIC_TYPE = "performancetest_duration"

    async def test_missing_duration(self):
        """Test that the performancetest duration is 0 if there is no duration in the HTML."""
        response = await self.collect(get_request_text="<span/>")
        self.assert_measurement(response, value="0")

    async def test_duration(self):
        """Test the performancetest duration."""
        response = await self.collect(
            get_request_text="""
            <span class="simulation-information-item">
                <span class="simulation-information-label">Duration: </span>
                <span>4m 14s </span>
            </span>"""
        )
        self.assert_measurement(response, value="4")
