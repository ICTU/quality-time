"""Unit tests for the JMeter CSV time passed collector."""

from datetime import datetime

from collector_utilities.functions import days_ago

from .base import JMeterCSVTestCase


class PerformanceTestRunnerTimePassedTest(JMeterCSVTestCase):
    """Unit tests for the JMeter CSV time passed collector."""

    METRIC_TYPE = "time_passed"
    METRIC_ADDITION = "max"

    async def test_no_transactions(self):
        """Test that the age is 0 if there are no transactions in the CSV."""
        response = await self.collect(get_request_text=self.JMETER_CSV.splitlines()[0])
        self.assert_measurement(response, value="0")

    async def test_time_passed(self):
        """Test that the test age is returned."""
        response = await self.collect(get_request_text=self.JMETER_CSV)
        expected_age = days_ago(datetime.utcfromtimestamp(1638325618779 / 1000.0))
        self.assert_measurement(response, value=str(expected_age))
