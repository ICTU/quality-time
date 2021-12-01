"""Unit tests for the JMeter JSON slow transactions collector."""

from .base import JMeterJSONTestCase


class JMeterJSONSlowTransactionsTest(JMeterJSONTestCase):
    """Unit tests for the JMeter JSON slow transactions collector."""

    METRIC_TYPE = "slow_transactions"

    def setUp(self):
        """Extend to set the expected entities."""
        super().setUp()
        self.expected_entities = [
            dict(
                key="-api-foo",
                name=self.API1,
                sample_count=123,
                error_count=2,
                error_percentage=round(2 / 123, 1),
                mean_response_time=110.0,
                median_response_time=120.0,
                min_response_time=50.0,
                max_response_time=250.0,
                percentile_90_response_time=115.0,
            ),
            dict(
                key="-api-bar",
                name=self.API2,
                sample_count=125,
                error_count=4,
                error_percentage=round(4 / 125, 1),
                mean_response_time=110.6,
                median_response_time=130.0,
                min_response_time=40.0,
                max_response_time=2500.0,
                percentile_90_response_time=120.0,
            ),
        ]
        self.set_source_parameter("target_response_time", "10")

    async def test_no_transactions(self):
        """Test that the number of slow transactions is 0 if there are no transactions in the JSON."""
        response = await self.collect(get_request_json_return_value={})
        self.assert_measurement(response, value="0")

    async def test_all_transactions(self):
        """Test retrieving all transaction."""
        response = await self.collect(get_request_json_return_value=self.JMETER_JSON)
        self.assert_measurement(response, value="2", entities=self.expected_entities)

    async def test_ignore_transaction(self):
        """Test that a transaction can be ignored."""
        self.set_source_parameter("transactions_to_ignore", [self.API2])
        response = await self.collect(get_request_json_return_value=self.JMETER_JSON)
        self.assert_measurement(response, value="1", entities=self.expected_entities[:1])

    async def test_include_transaction(self):
        """Test that a transaction can be included."""
        self.set_source_parameter("transactions_to_include", [self.API1])
        response = await self.collect(get_request_json_return_value=self.JMETER_JSON)
        self.assert_measurement(response, value="1", entities=self.expected_entities[:1])

    async def test_evaluate_different_response_time(self):
        """Test that a different response time type can be evaluated against the target response time."""
        self.set_source_parameter("response_time_to_evaluate", "min_response_time")
        self.set_source_parameter("target_response_time", "45")
        response = await self.collect(get_request_json_return_value=self.JMETER_JSON)
        self.assert_measurement(response, value="1", entities=self.expected_entities[:1])

    async def test_transaction_specific_response_time_target(self):
        """Test that a transaction specific target response time can be set."""
        self.set_source_parameter("transaction_specific_target_response_times", [".*bar:150"])
        response = await self.collect(get_request_json_return_value=self.JMETER_JSON)
        self.assert_measurement(response, value="1", entities=self.expected_entities[:1])
