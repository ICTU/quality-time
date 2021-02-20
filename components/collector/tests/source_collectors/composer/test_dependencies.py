"""Unit tests for the Composer dependencies collector."""

from ..source_collector_test_case import SourceCollectorTestCase


class ComposerDependenciesTest(SourceCollectorTestCase):
    """Unit tests for the Composer dependencies collector."""

    SOURCE_TYPE = "composer"
    METRIC_TYPE = "dependencies"

    def setUp(self):
        """Extend to set up the test fixtures."""
        super().setUp()
        self.composer_json = dict(
            installed=[
                {
                    "name": "package-1",
                    "version": "2.5.2",
                    "latest": "2.6.1",
                    "latest-status": "semver-safe-update",
                    "homepage": "https://url",
                    "description": "description",
                    "warning": "warning",
                },
                {"name": "package-2", "version": "2.0.0", "latest": "2.0.0", "latest-status": "up-to-date"},
            ]
        )
        self.expected_entities = [
            dict(
                key="package-1@2_5_2",
                name="package-1",
                version="2.5.2",
                latest="2.6.1",
                homepage="https://url",
                latest_status="semver-safe-update",
                description="description",
                warning="warning",
            ),
            dict(
                key="package-2@2_0_0",
                name="package-2",
                version="2.0.0",
                latest="2.0.0",
                homepage="",
                latest_status="up-to-date",
                description="",
                warning="",
            ),
        ]

    async def test_dependencies(self):
        """Test that the number of dependencies is returned."""
        response = await self.collect(get_request_json_return_value=self.composer_json)
        self.assert_measurement(response, value="2", total="2", entities=self.expected_entities)

    async def test_dependencies_by_status(self):
        """Test that the number of dependencies can be filtered by status."""
        self.set_source_parameter("latest_version_status", ["safe update possible"])
        response = await self.collect(get_request_json_return_value=self.composer_json)
        self.assert_measurement(response, value="1", total="2", entities=self.expected_entities[:1])
