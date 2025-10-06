"""Unit tests for the Dependency-Track security warnings collector."""

from source_collectors.dependency_track.dependencies import DependencyTrackComponent

from .base_test import DependencyTrackTestCase


class DependencyTrackDependenciesTest(DependencyTrackTestCase):
    """Unit tests for the Dependency-Track dependencies collector."""

    METRIC_TYPE = "dependencies"

    def dependencies(self, latest_version: str) -> list[DependencyTrackComponent]:
        """Create a list of dependencies as returned by Dependency-Track."""
        dependency: DependencyTrackComponent = {
            "name": "component name",
            "project": self.projects()[0],
            "version": "1.0",
            "uuid": "component-uuid",
        }
        if latest_version:
            dependency["repositoryMeta"] = {"latestVersion": latest_version}
        return [dependency]

    def entities(self, latest_version: str, latest_version_status: str) -> list[dict[str, str]]:
        """Create a list of expected entities."""
        return [
            {
                "component": "component name",
                "component_landing_url": f"{self.landing_url}/components/component-uuid",
                "key": "component-uuid",
                "latest": latest_version,
                "latest_version_status": latest_version_status,
                "project": "project name",
                "project_landing_url": f"{self.landing_url}/projects/project uuid",
                "project_version": "1.4",
                "version": "1.0",
            },
        ]

    async def test_no_projects(self):
        """Test that there are no dependencies if there are no projects."""
        response = await self.collect(get_request_json_return_value=[])
        self.assert_no_projects_found(response)

    async def test_no_vulnerabilities(self):
        """Test one project without dependencies."""
        response = await self.collect(get_request_json_side_effect=[self.projects(), []])
        self.assert_measurement(response, value="0", entities=[])

    async def test_updateable_dependencies(self):
        """Test one project with a component that can be updated."""
        response = await self.collect(get_request_json_side_effect=[self.projects(), self.dependencies("1.1")])
        self.assert_measurement(response, value="1", entities=self.entities("1.1", "update possible"))

    async def test_up_to_date_dependencies(self):
        """Test one project with a component that is up to date."""
        response = await self.collect(get_request_json_side_effect=[self.projects(), self.dependencies("1.0")])
        self.assert_measurement(response, value="1", entities=self.entities("1.0", "up-to-date"))

    async def test_unknown_latest_version(self):
        """Test one project with a component whose latest version is unknown."""
        response = await self.collect(get_request_json_side_effect=[self.projects(), self.dependencies("")])
        self.assert_measurement(response, value="1", entities=self.entities("unknown", "unknown"))

    async def test_filter_by_latest_version_status_with_match(self):
        """Test that components can be filtered by latest version status."""
        self.set_source_parameter("latest_version_status", ["up-to-date"])
        response = await self.collect(get_request_json_side_effect=[self.projects(), self.dependencies("1.0")])
        self.assert_measurement(response, value="1", entities=self.entities("1.0", "up-to-date"))

    async def test_filter_by_latest_version_status_without_match(self):
        """Test that components can be filtered by latest version status."""
        self.set_source_parameter("latest_version_status", ["update possible"])
        response = await self.collect(get_request_json_side_effect=[self.projects(), self.dependencies("1.0")])
        self.assert_measurement(response, value="0", entities=[])

    async def test_filter_by_project_name_with_match(self):
        """Test filtering projects by name and match."""
        self.set_source_parameter("project_names", ["project name", "other project"])
        response = await self.collect(get_request_json_side_effect=[self.projects(), self.dependencies("1.0")])
        self.assert_measurement(response, value="1", entities=self.entities("1.0", "up-to-date"))

    async def test_filter_by_project_name_without_match(self):
        """Test filtering projects by name without match."""
        self.set_source_parameter("project_names", ["other project"])
        response = await self.collect(get_request_json_return_value=self.projects())
        self.assert_no_projects_found(response)

    async def test_filter_by_project_regular_expression(self):
        """Test filtering projects by regular expression."""
        self.set_source_parameter("project_names", ["project .*"])
        response = await self.collect(get_request_json_side_effect=[self.projects(), self.dependencies("1.0")])
        self.assert_measurement(response, value="1", entities=self.entities("1.0", "up-to-date"))

    async def test_filter_by_project_version_with_match(self):
        """Test filtering projects by version with a match."""
        self.set_source_parameter("project_versions", ["1.2", "1.3", "1.4"])
        response = await self.collect(get_request_json_side_effect=[self.projects(), self.dependencies("1.0")])
        self.assert_measurement(response, value="1", entities=self.entities("1.0", "up-to-date"))

    async def test_filter_by_project_version_without_match(self):
        """Test filtering projects by version without a match."""
        self.set_source_parameter("project_versions", ["1.2", "1.3"])
        response = await self.collect(get_request_json_return_value=self.projects())
        self.assert_no_projects_found(response)

    async def test_filter_by_project_name_and_version(self):
        """Test filtering projects by name and version."""
        self.set_source_parameter("project_names", ["project .*"])
        self.set_source_parameter("project_versions", ["1.3", "1.4"])
        response = await self.collect(get_request_json_side_effect=[self.projects(), self.dependencies("1.0")])
        self.assert_measurement(response, value="1", entities=self.entities("1.0", "up-to-date"))

    async def test_filter_by_project_version_when_project_has_no_version(self):
        """Test filtering projects by version."""
        self.set_source_parameter("project_versions", ["1.2", "1.3"])
        response = await self.collect(get_request_json_return_value=self.projects(version=""))
        self.assert_no_projects_found(response)

    async def test_filter_by_latest_project(self):
        """Test that projects can be filtered by being the latest project version."""
        self.set_source_parameter("only_include_latest_project_versions", "yes")
        response = await self.collect(get_request_json_side_effect=[self.projects()])
        self.assert_no_projects_found(response)
