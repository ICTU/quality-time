"""Unit tests for the JMeter CSV performance test duration collector."""

from .base import JMeterCSVTestCase


class JMeterCSVPerformancetestDurationTest(JMeterCSVTestCase):
    """Unit tests for the JMeter CSV performancetest duration collector."""

    METRIC_TYPE = "performancetest_duration"

    async def test_no_transactions(self):
        """Test that the performancetest duration is 0 if there are no transactions in the CSV."""
        response = await self.collect(get_request_text=self.JMETER_CSV.splitlines()[0])
        self.assert_measurement(response, value="0")

    async def test_all_transactions(self):
        """Test the performancetest duration of all transactions in the CSV."""
        response = await self.collect(get_request_text=self.JMETER_CSV)
        self.assert_measurement(response, value="2")
