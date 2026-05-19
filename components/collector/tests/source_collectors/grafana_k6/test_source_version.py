"""Unit tests for the Grafana k6 source version collector."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class GrafanaK6SourceVersionTest(SourceCollectorTestCase):
    """Unit tests for the Grafana k6 source version collector."""

    METRIC_TYPE = "source_version"
    SOURCE_TYPE = "grafana_k6"

    async def test_missing_metadata_gives_parse_error(self):
        """Test that a parse error is returned if the JSON has no metadata."""
        json = {}
        measurement = await self.collect_measurement(get_request_json_return_value=json)
        self.assert_measurement(measurement, parse_error="Could not find an object")

    async def test_missing_generated_at_gives_parse_error(self):
        """Test that a parse error is returned if the JSON has no k6Version in the metadata."""
        json = {"metadata": {}}
        measurement = await self.collect_measurement(get_request_json_return_value=json)
        self.assert_measurement(measurement, parse_error="Could not find an object")

    async def test_source_version(self):
        """Test the source version."""
        json = {"metadata": {"k6Version": (k6_version := "1.10")}}
        measurement = await self.collect_measurement(get_request_json_return_value=json)
        self.assert_measurement(measurement, value=k6_version)

    async def test_source_version_with_snake_case_key(self):
        """Test the source version when k6 uses the snake_case "k6_version" key (k6 v1.7.x)."""
        json = {"metadata": {"k6_version": (k6_version := "1.7.1")}}
        measurement = await self.collect_measurement(get_request_json_return_value=json)
        self.assert_measurement(measurement, value=k6_version)
