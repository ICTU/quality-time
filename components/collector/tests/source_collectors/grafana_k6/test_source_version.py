"""Unit tests for the Grafana k6 source version collector."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class GrafanaK6SourceVersionTest(SourceCollectorTestCase):
    """Unit tests for the Grafana k6 source version collector."""

    METRIC_TYPE = "source_version"
    SOURCE_TYPE = "grafana_k6"

    async def test_missing_metadata_gives_parse_error(self):
        """Test that a parse error is returned if the JSON has no metadata."""
        response = await self.collect(get_request_json_return_value={})
        self.assert_measurement(response, parse_error="Could not find an object")

    async def test_missing_generated_at_gives_parse_error(self):
        """Test that a parse error is returned if the JSON has no k6Version in the metadata."""
        response = await self.collect(get_request_json_return_value={"metadata": {}})
        self.assert_measurement(response, parse_error="Could not find an object")

    async def test_source_version(self):
        """Test the source version."""
        k6_version = "1.1.0"
        response = await self.collect(get_request_json_return_value={"metadata": {"k6Version": k6_version}})
        self.assert_measurement(response, value=k6_version)
