"""Unit tests for the manual version source."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class ManualVersionTest(SourceCollectorTestCase):
    """Unit tests for the manual version collectors."""

    SOURCE_TYPE = "manual_version"
    METRIC_TYPE = "source_version"

    async def test_source_version(self):
        """Test the source version."""
        self.set_source_parameter("version", "1.3.4")
        measurement = await self.collect_measurement()
        self.assert_measurement(measurement, value="1.3.4")

    async def test_invalid_source_version(self):
        """Test an invalud source version."""
        self.set_source_parameter("version", "invalid")
        measurement = await self.collect_measurement()
        self.assert_measurement(measurement, parse_error="Invalid version: 'invalid'")
