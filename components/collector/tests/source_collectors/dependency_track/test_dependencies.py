"""Unit tests for the Dependency-Track security warnings collector."""

from source_collectors.dependency_track.dependencies import DependencyTrackComponent

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class DependencyTrackDependenciesTest(SourceCollectorTestCase):
    """Unit tests for the Dependency-Track dependencies collector."""

    METRIC_TYPE = "dependencies"
    SOURCE_TYPE = "dependency_track"

    def setUp(self) -> None:
        """Extend to set up Dependency-Track projects."""
        super().setUp()
        self.projects = [{"uuid": "project uuid", "name": "project name"}]

    def create_dependencies(self, latest_version: str) -> list[DependencyTrackComponent]:
        """Create a list of dependencies as returned by Dependency-Track."""
        dependency: DependencyTrackComponent = {
            "name": "component name",
            "project": {"name": "project name", "uuid": "project uuid"},
            "uuid": "component-uuid",
            "version": "1.0",
        }
        if latest_version:
            dependency["repositoryMeta"] = {"latestVersion": latest_version}
        return [dependency]

    def create_entities(self, latest_version: str, latest_version_status: str) -> list[dict[str, str]]:
        """Create a list of expected entities."""
        return [
            {
                "component": "component name",
                "component_landing_url": "/components/component-uuid",
                "key": "component-uuid",
                "latest": latest_version,
                "latest_version_status": latest_version_status,
                "project": "project name",
                "project_landing_url": "/projects/project uuid",
                "version": "1.0",
            },
        ]

    async def test_no_projects(self):
        """Test that there are no dependencies if there are no projects."""
        response = await self.collect(get_request_json_return_value=[])
        self.assert_measurement(response, value="0", entities=[])

    async def test_no_vulnerabilities(self):
        """Test one project without dependencies."""
        response = await self.collect(get_request_json_side_effect=[self.projects, []])
        self.assert_measurement(response, value="0", entities=[])

    async def test_updateable_dependencies(self):
        """Test one project with a component that can be updated."""
        response = await self.collect(get_request_json_side_effect=[self.projects, self.create_dependencies("1.1")])
        self.assert_measurement(response, value="1", entities=self.create_entities("1.1", "update possible"))

    async def test_up_to_date_dependencies(self):
        """Test one project with a component that is up to date."""
        response = await self.collect(get_request_json_side_effect=[self.projects, self.create_dependencies("1.0")])
        self.assert_measurement(response, value="1", entities=self.create_entities("1.0", "up-to-date"))

    async def test_unknown_latest_version(self):
        """Test one project with a component whose latest version is unknown."""
        response = await self.collect(get_request_json_side_effect=[self.projects, self.create_dependencies("")])
        self.assert_measurement(response, value="1", entities=self.create_entities("unknown", "unknown"))

    async def test_filter_by_latest_version_status(self):
        """Test that components can be filtered by latest version status."""
        self.set_source_parameter("latest_version_status", ["update possible"])
        response = await self.collect(get_request_json_side_effect=[self.projects, self.create_dependencies("1.0")])
        self.assert_measurement(response, value="0", entities=[])
