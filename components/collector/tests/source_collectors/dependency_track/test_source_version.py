"""Unit tests for the Dependency-Track source version collector."""

from .base_test import DependencyTrackTestCase


class DependencyTrackSourceVersionTest(DependencyTrackTestCase):
    """Unit tests for the Dependency-Track source version collector."""

    METRIC_TYPE = "source_version"

    async def test_source_version(self):
        """Test that the source version can be measured."""
        measurement = await self.collect_measurement(get_request_json_return_value={"version": "4.8.2"})
        self.assert_measurement(measurement, value="4.8.2", landing_url=self.landing_url)
