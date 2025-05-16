"""Unit tests for the Grafana k6 slow transactions collector."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class GrafanaK6SlowTransactionsTest(SourceCollectorTestCase):
    """Unit tests for the Grafana k6 slow transactions collector."""

    METRIC_TYPE = "performancetest_duration"
    SOURCE_TYPE = "grafana_k6"

    async def test_missing_state_gives_parse_error(self):
        """Test that a parse error is returned if the JSON has no state."""
        response = await self.collect(get_request_json_return_value={})
        self.assert_measurement(response, parse_error="Could not find an object")

    async def test_missing_duration_gives_parse_error(self):
        """Test that a parse error is returned if the JSON has no duration."""
        response = await self.collect(get_request_json_return_value={"state": {}})
        self.assert_measurement(response, parse_error="Could not find an object")

    async def test_duration(self):
        """Test that the duration."""
        response = await self.collect(get_request_json_return_value={"state": {"testRunDurationMs": 1040803.440334}})
        self.assert_measurement(response, value="17")
