"""Unit tests for the JMeter JSON slow transactions collector."""

from ..source_collector_test_case import SourceCollectorTestCase


class JMeterJSONSlowTransactionsTest(SourceCollectorTestCase):
    """Unit tests for the JMeter JSON slow transactions collector."""

    METRIC_TYPE = "slow_transactions"
    SOURCE_TYPE = "jmeter_json"
    JMETER_JSON = json = dict(
        transaction1=dict(
            transaction="/api/foo",
            sampleCount=123,
            errorCount=2,
            errorPct=2 / 123,
            meanResTime=110,
            medianResTime=120,
            minResTime=50.0,
            maxResTime=250.0000004,
            pct1ResTime=115.0,
        ),
        transaction2=dict(
            transaction="/api/bar",
            sampleCount=125,
            errorCount=4,
            errorPct=4 / 125,
            meanResTime=110.56,
            medianResTime=130,
            minResTime=40.0,
            maxResTime=2500.03223,
            pct1ResTime=120.0,
        ),
        Total={},  # Total should be ignored
    )

    def setUp(self):
        """Extend to set the expected entities."""
        super().setUp()
        self.expected_entities = [
            dict(
                key="-api-foo",
                name="/api/foo",
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
                name="/api/bar",
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
        self.set_source_parameter("transactions_to_ignore", ["/api/bar"])
        response = await self.collect(get_request_json_return_value=self.JMETER_JSON)
        self.assert_measurement(response, value="1", entities=self.expected_entities[:1])

    async def test_include_transaction(self):
        """Test that a transaction can be included."""
        self.set_source_parameter("transactions_to_include", ["/api/foo"])
        response = await self.collect(get_request_json_return_value=self.JMETER_JSON)
