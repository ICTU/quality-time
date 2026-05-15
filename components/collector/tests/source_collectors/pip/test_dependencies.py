"""Unit tests for the pip dependencies collector."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class PipDependenciesTest(SourceCollectorTestCase):
    """Unit tests for the dependencies collector."""

    SOURCE_TYPE = "pip"
    METRIC_TYPE = "dependencies"

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.pip_json = [
            {"name": "gitdb2", "version": "2.0.6", "latest_version": "4.0.2", "latest_filetype": "wheel"},
            {"name": "requests", "version": "14.0.6", "latest_version": "14.1.2", "latest_filetype": "wheel"},
            {"name": "pip", "version": "20.1", "latest_version": "20.1.1", "latest_filetype": "wheel"},
        ]

    def expected_entities(self, *names: str) -> list[dict[str, str]]:
        """Return the expected entities."""
        all_entities = [
            {"key": "gitdb2@2_0_6", "name": "gitdb2", "version": "2.0.6", "latest": "4.0.2"},
            {"key": "requests@14_0_6", "name": "requests", "version": "14.0.6", "latest": "14.1.2"},
            {"key": "pip@20_1", "name": "pip", "version": "20.1", "latest": "20.1.1"},
        ]
        return [entity for entity in all_entities if entity["name"] in names]

    async def test_dependencies(self):
        """Test that the number of dependencies is returned."""
        expected_entities = self.expected_entities("gitdb2", "requests", "pip")
        measurement = await self.collect_measurement(get_request_json_return_value=self.pip_json)
        self.assert_measurement(measurement, value="3", total="3", entities=expected_entities)

    async def test_filter_dependencies(self):
        """Test that the dependencies can be filtered by update type."""
        self.set_source_parameter("updates_to_include", ["major", "minor"])
        expected_entities = self.expected_entities("gitdb2", "requests")
        measurement = await self.collect_measurement(get_request_json_return_value=self.pip_json)
        self.assert_measurement(measurement, value="2", total="3", entities=expected_entities)
