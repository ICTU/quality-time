"""Unit tests for the JMeter JSON tests collector."""

from .base import JMeterJSONTestCase


class JMeterJSONTestsTest(JMeterJSONTestCase):
    """Unit tests for the JMeter JSON tests collector."""

    METRIC_TYPE = "tests"

    async def test_no_transactions(self):
        """Test that the number of tests is 0 if there are no transactions in the JSON."""
        response = await self.collect(get_request_json_return_value={})
        self.assert_measurement(response, value="0")

    async def test_all_samples(self):
        """Test retrieving all samples."""
        response = await self.collect(get_request_json_return_value=self.JMETER_JSON)
        self.assert_measurement(response, value="248", entities=[])

    async def test_failed_samples(self):
        """Test retrieving the failed samples."""
        self.set_source_parameter("test_result", ["failed"])
        response = await self.collect(get_request_json_return_value=self.JMETER_JSON)
        self.assert_measurement(response, value="6", entities=[])

    async def test_successful_samples(self):
        """Test retrieving the successful samples."""
        self.set_source_parameter("test_result", ["success"])
        response = await self.collect(get_request_json_return_value=self.JMETER_JSON)
        self.assert_measurement(response, value="242", entities=[])

    async def test_ignore_transaction(self):
        """Test that a transaction can be ignored."""
        self.set_source_parameter("transactions_to_ignore", [self.API2])
        response = await self.collect(get_request_json_return_value=self.JMETER_JSON)
        self.assert_measurement(response, value="123", entities=[])

    async def test_include_transaction(self):
        """Test that a transaction can be included."""
        self.set_source_parameter("transactions_to_include", [self.API1])
        response = await self.collect(get_request_json_return_value=self.JMETER_JSON)
        self.assert_measurement(response, value="123", entities=[])
