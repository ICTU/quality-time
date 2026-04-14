"""Unit tests for the manual version source."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class ManualVersionTest(SourceCollectorTestCase):
    """Unit tests for the manual version collectors."""

    SOURCE_TYPE = "manual_version"
    METRIC_TYPE = "source_version"

    async def test_source_version(self):
        """Test the source version."""
        self.set_source_parameter("version", "1.3.4")
        response = await self.collect()
        self.assert_measurement(response, value="1.3.4")

    async def test_invalid_source_version(self):
        """Test an invalud source version."""
        self.set_source_parameter("version", "invalid")
        response = await self.collect()
        self.assert_measurement(response, parse_error="Invalid version: 'invalid'")
