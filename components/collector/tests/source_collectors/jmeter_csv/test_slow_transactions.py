"""Unit tests for the JMeter CSV slow transactions collector."""

from .base import JMeterCSVTestCase


class JMeterCSVSlowTransactionsTest(JMeterCSVTestCase):
    """Unit tests for the JMeter CSV slow transactions collector."""

    METRIC_TYPE = "slow_transactions"

    def setUp(self):
        """Extend to set the expected entities."""
        super().setUp()
        self.expected_entities = [
            dict(
                key="-api-search",
                name="/api/search",
                sample_count=2,
                error_count=0,
                error_percentage=0.0,
                mean_response_time=(mean := round((1207 + 359) / 2, 1)),
                median_response_time=mean,  # median == mean due to small number of samples
                min_response_time=359.0,
                max_response_time=1207.0,
                percentile_90_response_time=1800.6,
            ),
            dict(
                key="-home",
                name="/home",
                sample_count=2,
                error_count=1,
                error_percentage=0.5,
                mean_response_time=(mean := round((10 + 54) / 2, 1)),
                median_response_time=mean,  # median == mean due to small number of samples
                min_response_time=10.0,
                max_response_time=54.0,
                percentile_90_response_time=84.8,
            ),
        ]
        self.set_source_parameter("target_response_time", "10")

    async def test_no_transactions(self):
        """Test that the number of slow transactions is 0 if there are no transactions in the CSV."""
        response = await self.collect(get_request_text=self.JMETER_CSV.splitlines()[0])
        self.assert_measurement(response, value="0")

    async def test_all_transactions(self):
        """Test retrieving all transaction."""
        response = await self.collect(get_request_text=self.JMETER_CSV)
        self.assert_measurement(response, value="2", entities=self.expected_entities)

    async def test_ignore_transaction(self):
        """Test that a transaction can be ignored."""
        self.set_source_parameter("transactions_to_ignore", ["/home"])
        response = await self.collect(get_request_text=self.JMETER_CSV)
        self.assert_measurement(response, value="1", entities=self.expected_entities[:1])

    async def test_include_transaction(self):
        """Test that a transaction can be included."""
        self.set_source_parameter("transactions_to_include", ["/api/search"])
        response = await self.collect(get_request_text=self.JMETER_CSV)
        self.assert_measurement(response, value="1", entities=self.expected_entities[:1])

    async def test_evaluate_different_response_time(self):
        """Test that a different response time type can be evaluated against the target response time."""
        self.set_source_parameter("response_time_to_evaluate", "min_response_time")
        self.set_source_parameter("target_response_time", "45")
        response = await self.collect(get_request_text=self.JMETER_CSV)
        self.assert_measurement(response, value="1", entities=self.expected_entities[:1])

    async def test_transaction_specific_response_time_target(self):
        """Test that a transaction specific target response time can be set."""
        self.set_source_parameter("transaction_specific_target_response_times", [".*home:100"])
        response = await self.collect(get_request_text=self.JMETER_CSV)
        self.assert_measurement(response, value="1", entities=self.expected_entities[:1])
