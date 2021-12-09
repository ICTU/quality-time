"""Unit tests for the JMeter CSV tests collector."""

from .base import JMeterCSVTestCase


class JMeterCSVTestsTest(JMeterCSVTestCase):
    """Unit tests for the JMeter CSV tests collector."""

    METRIC_TYPE = "tests"

    async def test_no_transactions(self):
        """Test that the number of tests is 0 if there are no transactions in the CSV."""
        response = await self.collect(get_request_text=self.JMETER_CSV.splitlines()[0])
        self.assert_measurement(response, value="0")

    async def test_all_samples(self):
        """Test retrieving all samples."""
        response = await self.collect(get_request_text=self.JMETER_CSV)
        self.assert_measurement(response, value="4", entities=[])

    async def test_failed_samples(self):
        """Test retrieving the failed samples."""
        self.set_source_parameter("test_result", ["failed"])
        response = await self.collect(get_request_text=self.JMETER_CSV)
        self.assert_measurement(response, value="1", entities=[])

    async def test_successful_samples(self):
        """Test retrieving the successful samples."""
        self.set_source_parameter("test_result", ["success"])
        response = await self.collect(get_request_text=self.JMETER_CSV)
        self.assert_measurement(response, value="3", entities=[])

    async def test_ignore_transaction(self):
        """Test that a transaction can be ignored."""
        self.set_source_parameter("transactions_to_ignore", ["/home"])
        response = await self.collect(get_request_text=self.JMETER_CSV)
        self.assert_measurement(response, value="2", entities=[])

    async def test_include_transaction(self):
        """Test that a transaction can be included."""
        self.set_source_parameter("transactions_to_include", ["/home"])
        response = await self.collect(get_request_text=self.JMETER_CSV)
        self.assert_measurement(response, value="2", entities=[])
