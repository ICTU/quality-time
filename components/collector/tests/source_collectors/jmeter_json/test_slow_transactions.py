"""Unit tests for the JMeter JSON slow transactions collector."""

from ..source_collector_test_case import SourceCollectorTestCase


class JMeterJSONSlowTransactionsTest(SourceCollectorTestCase):
    """Unit tests for the JMeter JSON slow transactions collector."""

    METRIC_TYPE = "slow_transactions"
    SOURCE_TYPE = "jmeter_json"

    async def test_no_transactions(self):
        """Test that the number of slow transactions is 0 if there are no transactions in the JSON."""
        response = await self.collect(get_request_json_return_value={})
        self.assert_measurement(response, value="0")

    async def test_one_transactions(self):
        """Test one transaction."""
        json = dict(
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
            Total={},  # Total should be ignored
        )
        response = await self.collect(get_request_json_return_value=json)
        expected_entities = [
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
            )
        ]
        self.assert_measurement(response, value="1", entities=expected_entities)
