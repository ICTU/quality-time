"""Unit tests for the Dependency-Track dependencies collector."""

from typing import TYPE_CHECKING

from source_collectors.dependency_track.json_types import DependencyTrackProject

from .base_test import DependencyTrackTestCase

if TYPE_CHECKING:
    from model.measurement import MetricMeasurement
    from source_collectors.dependency_track.json_types import DependencyTrackComponent


class DependencyTrackDependenciesTest(DependencyTrackTestCase):
    """Unit tests for the Dependency-Track dependencies collector."""

    METRIC_TYPE = "dependencies"

    def dependencies(self, latest_version: str) -> list[DependencyTrackComponent]:
        """Create a list of dependencies as returned by Dependency-Track."""
        dependency = self.component()
        if latest_version:
            dependency["repositoryMeta"] = {"latestVersion": latest_version}
        return [dependency]

    def entity(self, name: str = "component name", uuid: str = "component-uuid", **attributes) -> dict[str, str]:
        """Create an expected entity for the component with the specified name and UUID."""
        return {
            "component": name,
            "component_landing_url": f"{self.landing_url}/components/{uuid}",
            "key": uuid,
            "latest": "unknown",
            "latest_version_status": "unknown",
            "project": "project name",
            "project_landing_url": f"{self.landing_url}/projects/project uuid",
            "project_version": "1.4",
            "root_component": "",
            "version": "1.0",
        } | attributes

    def entities(self, latest_version: str, latest_version_status: str) -> list[dict[str, str]]:
        """Create a list of expected entities."""
        return [self.entity(latest=latest_version, latest_version_status=latest_version_status)]

    async def collect_components(self, components: list[DependencyTrackComponent]) -> MetricMeasurement:
        """Collect a measurement for the given components."""
        return await self.collect_measurement(get_request_json_side_effect=[self.projects(), components])

    async def test_no_projects(self):
        """Test that there are no dependencies if there are no projects."""
        measurement = await self.collect_measurement(get_request_json_return_value=[])
        self.assert_no_projects_found(measurement)

    async def test_no_vulnerabilities(self):
        """Test one project without dependencies."""
        measurement = await self.collect_measurement(get_request_json_side_effect=[self.projects(), []])
        self.assert_measurement(measurement, value="0", entities=[])

    async def test_updateable_dependencies(self):
        """Test one project with a component that can be updated."""
        measurement = await self.collect_measurement(
            get_request_json_side_effect=[self.projects(), self.dependencies("1.1")]
        )
        self.assert_measurement(measurement, value="1", entities=self.entities("1.1", "update possible"))

    async def test_up_to_date_dependencies(self):
        """Test one project with a component that is up to date."""
        measurement = await self.collect_measurement(
            get_request_json_side_effect=[self.projects(), self.dependencies("1.0")]
        )
        self.assert_measurement(measurement, value="1", entities=self.entities("1.0", "up-to-date"))

    async def test_unknown_latest_version(self):
        """Test one project with a component whose latest version is unknown."""
        measurement = await self.collect_measurement(
            get_request_json_side_effect=[self.projects(), self.dependencies("")]
        )
        self.assert_measurement(measurement, value="1", entities=self.entities("unknown", "unknown"))

    async def test_filter_by_latest_version_status_with_match(self):
        """Test that components can be filtered by latest version status."""
        self.set_source_parameter("latest_version_status", ["up-to-date"])
        measurement = await self.collect_measurement(
            get_request_json_side_effect=[self.projects(), self.dependencies("1.0")]
        )
        self.assert_measurement(measurement, value="1", entities=self.entities("1.0", "up-to-date"))

    async def test_filter_by_latest_version_status_without_match(self):
        """Test that components can be filtered by latest version status."""
        self.set_source_parameter("latest_version_status", ["update possible"])
        measurement = await self.collect_measurement(
            get_request_json_side_effect=[self.projects(), self.dependencies("1.0")]
        )
        self.assert_measurement(measurement, value="0", entities=[])

    async def test_filter_by_project_name_with_match(self):
        """Test filtering projects by name and match."""
        self.set_source_parameter("project_names", ["project name", "other project"])
        measurement = await self.collect_measurement(
            get_request_json_side_effect=[self.projects(), self.dependencies("1.0")]
        )
        self.assert_measurement(measurement, value="1", entities=self.entities("1.0", "up-to-date"))

    async def test_filter_by_project_name_without_match(self):
        """Test filtering projects by name without match."""
        self.set_source_parameter("project_names", ["other project"])
        measurement = await self.collect_measurement(get_request_json_return_value=self.projects())
        self.assert_no_projects_found(measurement)

    async def test_filter_by_project_regular_expression(self):
        """Test filtering projects by regular expression."""
        self.set_source_parameter("project_names", ["project .*"])
        measurement = await self.collect_measurement(
            get_request_json_side_effect=[self.projects(), self.dependencies("1.0")]
        )
        self.assert_measurement(measurement, value="1", entities=self.entities("1.0", "up-to-date"))

    async def test_filter_by_project_version_with_match(self):
        """Test filtering projects by version with a match."""
        self.set_source_parameter("project_versions", ["1.2", "1.3", "1.4"])
        measurement = await self.collect_measurement(
            get_request_json_side_effect=[self.projects(), self.dependencies("1.0")]
        )
        self.assert_measurement(measurement, value="1", entities=self.entities("1.0", "up-to-date"))

    async def test_filter_by_project_version_without_match(self):
        """Test filtering projects by version without a match."""
        self.set_source_parameter("project_versions", ["1.2", "1.3"])
        measurement = await self.collect_measurement(get_request_json_return_value=self.projects())
        self.assert_no_projects_found(measurement)

    async def test_filter_by_project_name_and_version(self):
        """Test filtering projects by name and version."""
        self.set_source_parameter("project_names", ["project .*"])
        self.set_source_parameter("project_versions", ["1.3", "1.4"])
        measurement = await self.collect_measurement(
            get_request_json_side_effect=[self.projects(), self.dependencies("1.0")]
        )
        self.assert_measurement(measurement, value="1", entities=self.entities("1.0", "up-to-date"))

    async def test_filter_by_project_version_when_project_has_no_version(self):
        """Test filtering projects by version."""
        self.set_source_parameter("project_versions", ["1.2", "1.3"])
        measurement = await self.collect_measurement(get_request_json_return_value=self.projects(version=""))
        self.assert_no_projects_found(measurement)

    async def test_filter_by_latest_project(self):
        """Test that projects can be filtered by being the latest project version."""
        self.set_source_parameter("only_include_latest_project_versions", "yes")
        measurement = await self.collect_measurement(get_request_json_side_effect=[self.projects()])
        self.assert_no_projects_found(measurement)

    async def test_direct_dependency_has_no_root_component(self):
        """Test that a component the project depends on directly has no root component."""
        measurement = await self.collect_components([self.component(direct_dependencies=[])])
        self.assert_measurement(measurement, value="1", entities=[self.entity()])

    async def test_transitive_dependency(self):
        """Test that the root component of a transitive dependency is reported."""
        components = [
            self.component(name="parent", uuid="parent-uuid", direct_dependencies=["component-uuid"]),
            self.component(),
        ]
        measurement = await self.collect_components(components)
        self.assert_measurement(
            measurement,
            value="2",
            entities=[
                self.entity(name="parent", uuid="parent-uuid"),
                self.entity(**self.root_component_attributes("parent", "parent-uuid")),
            ],
        )

    async def test_deeply_nested_dependency(self):
        """Test that the root dependency is reported, and not the direct parent of the component."""
        components = [
            self.component(name="root", uuid="root-uuid", direct_dependencies=["intermediate-uuid"]),
            self.component(name="intermediate", uuid="intermediate-uuid", direct_dependencies=["component-uuid"]),
            self.component(),
        ]
        measurement = await self.collect_components(components)
        self.assert_measurement(
            measurement,
            value="3",
            entities=[
                self.entity(name="root", uuid="root-uuid"),
                self.entity(
                    name="intermediate",
                    uuid="intermediate-uuid",
                    **self.root_component_attributes("root", "root-uuid"),
                ),
                self.entity(**self.root_component_attributes("root", "root-uuid")),
            ],
        )

    async def test_multiple_root_components(self):
        """Test that all root components are reported, sorted by name, and without landing URL."""
        components = [
            self.component(name="root b", uuid="root-b-uuid", direct_dependencies=["component-uuid"]),
            self.component(name="root a", uuid="root-a-uuid", direct_dependencies=["component-uuid"]),
            self.component(),
        ]
        measurement = await self.collect_components(components)
        self.assert_measurement(
            measurement,
            value="3",
            entities=[
                self.entity(name="root b", uuid="root-b-uuid"),
                self.entity(name="root a", uuid="root-a-uuid"),
                self.entity(**self.root_component_attributes("root a, root b")),
            ],
        )

    async def test_cycle_in_the_dependency_graph(self):
        """Test that a cycle in the dependency graph does not cause an endless loop."""
        components = [
            self.component(name="root", uuid="root-uuid", direct_dependencies=["cycle-uuid"]),
            self.component(name="cycle", uuid="cycle-uuid", direct_dependencies=["component-uuid"]),
            self.component(direct_dependencies=["cycle-uuid"]),
        ]
        measurement = await self.collect_components(components)
        self.assert_measurement(
            measurement,
            value="3",
            entities=[
                self.entity(name="root", uuid="root-uuid"),
                self.entity(name="cycle", uuid="cycle-uuid", **self.root_component_attributes("root", "root-uuid")),
                self.entity(**self.root_component_attributes("root", "root-uuid")),
            ],
        )

    async def test_dependency_graph_without_edges(self):
        """Test that components without dependency graph have no root component."""
        components = [self.component(), self.component(name="other", uuid="other-uuid")]
        components[0]["directDependencies"] = None  # Dependency-Track returns null if there is no dependency graph
        measurement = await self.collect_components(components)
        self.assert_measurement(
            measurement,
            value="2",
            entities=[self.entity(), self.entity(name="other", uuid="other-uuid")],
        )

    async def test_dependency_on_a_service(self):
        """Test that a service that a component depends on does not become a root component."""
        components = [self.component(direct_dependencies=["service-uuid"])]
        measurement = await self.collect_components(components)
        self.assert_measurement(measurement, value="1", entities=[self.entity()])

    async def test_components_of_multiple_projects(self):
        """Test that each project has its own dependency graph."""
        other_project = DependencyTrackProject(name="other project", uuid="other-project-uuid", version="2.0")
        measurement = await self.collect_measurement(
            get_request_json_side_effect=[
                [*self.projects(), other_project],
                [
                    self.component(name="parent", uuid="parent-uuid", direct_dependencies=["component-uuid"]),
                    self.component(),
                ],
                [self.component(name="other", uuid="other-uuid", direct_dependencies=[], project=other_project)],
            ],
        )
        self.assert_measurement(
            measurement,
            value="3",
            entities=[
                self.entity(name="parent", uuid="parent-uuid"),
                self.entity(**self.root_component_attributes("parent", "parent-uuid")),
                self.entity(
                    name="other",
                    uuid="other-uuid",
                    project="other project",
                    project_landing_url=f"{self.landing_url}/projects/other-project-uuid",
                    project_version="2.0",
                ),
            ],
        )
