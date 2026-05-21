"""Unit tests for the Grafana k6 source up-to-dateness collector."""

from collector_utilities.date_time import days_ago, parse_datetime

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class GrafanaK6SourceUpToDatenessTest(SourceCollectorTestCase):
    """Unit tests for the Grafana k6 source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"
    SOURCE_TYPE = "grafana_k6"

    async def test_missing_metadata_gives_parse_error(self):
        """Test that a parse error is returned if the JSON has no metadata."""
        measurement = await self.collect_measurement(get_request_json_return_value={})
        self.assert_measurement(measurement, parse_error="Could not find an object")

    async def test_missing_generated_at_gives_parse_error(self):
        """Test that a parse error is returned if the JSON has no generatedAt in the metadata."""
        measurement = await self.collect_measurement(get_request_json_return_value={"metadata": {}})
        self.assert_measurement(measurement, parse_error="Could not find an object")

    async def test_source_up_to_dateness(self):
        """Test the source up-to-dateness."""
        generated_at = "2026-04-21T10:00:00.000Z"
        measurement = await self.collect_measurement(
            get_request_json_return_value={"metadata": {"generatedAt": generated_at}}
        )
        expected_value = str(days_ago(parse_datetime(generated_at)))
        self.assert_measurement(measurement, value=expected_value)

    async def test_source_up_to_dateness_with_snake_case_key(self):
        """Test the source up-to-dateness when k6 uses the snake_case "generated_at" key (k6 v1.7.x)."""
        generated_at = "2026-04-21T10:00:00.000Z"
        measurement = await self.collect_measurement(
            get_request_json_return_value={"metadata": {"generated_at": generated_at}}
        )
        expected_value = str(days_ago(parse_datetime(generated_at)))
        self.assert_measurement(measurement, value=expected_value)
