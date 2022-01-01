"""Unit tests for the Gatling log performance test duration collector."""

from .base import GatlingLogTestCase


class GatlingLogPerformancetestDurationTest(GatlingLogTestCase):
    """Unit tests for the Gatling log performancetest duration collector."""

    METRIC_TYPE = "performancetest_duration"

    async def test_no_transactions(self):
        """Test that the performancetest duration is 0 if there are no transactions in the log."""
        response = await self.collect(get_request_text="")
        self.assert_measurement(response, value="0")

    async def test_all_transactions(self):
        """Test the performancetest duration of all transactions in the CSV."""
        response = await self.collect(get_request_text=self.GATLING_LOG)
        self.assert_measurement(response, value="2")
