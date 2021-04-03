"""Unit tests for the Quality-time source version collector."""

from ..source_collector_test_case import SourceCollectorTestCase


class QualityTimeSourceVersionTest(SourceCollectorTestCase):
    """Unit tests for the Quality-time source version collector."""

    METRIC_TYPE = "source_version"
    METRIC_ADDITION = "min"
    SOURCE_TYPE = "quality_time"

    async def test_source_version(self):
        """Test that the source version can be measured."""
        response = await self.collect(get_request_json_return_value=dict(version="3.19.1"))
        self.assert_measurement(response, value="3.19.1", landing_url="https://quality_time")
