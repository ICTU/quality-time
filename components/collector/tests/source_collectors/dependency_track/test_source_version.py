"""Unit tests for the Dependency-Track source version collector."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class DependencyTrackSourceVersionTest(SourceCollectorTestCase):
    """Unit tests for the Dependency-Track source version collector."""

    METRIC_ADDITION = "min"
    METRIC_TYPE = "source_version"
    SOURCE_TYPE = "dependency_track"

    async def test_source_version(self):
        """Test that the source version can be measured."""
        response = await self.collect(get_request_json_return_value={"version": "4.8.2"})
        self.assert_measurement(response, value="4.8.2", landing_url="https://dependency_track")
