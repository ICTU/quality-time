"""Unit tests for the JMeter CSV source-up-to-dateness collector."""

from collector_utilities.date_time import days_ago, datetime_fromtimestamp

from .base import JMeterCSVTestCase


class PerformanceTestRunnerSourceUpToDatenessTest(JMeterCSVTestCase):
    """Unit tests for the JMeter CSV source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    async def test_no_transactions(self):
        """Test that the age is 0 if there are no transactions in the CSV."""
        response = await self.collect(get_request_text=self.JMETER_CSV.splitlines()[0])
        self.assert_measurement(response, value="0")

    async def test_source_up_to_dateness(self):
        """Test that the test age is returned."""
        response = await self.collect(get_request_text=self.JMETER_CSV)
        expected_age = days_ago(datetime_fromtimestamp(1638325618779 / 1000.0))
        self.assert_measurement(response, value=str(expected_age))
