"""Base classes for Dependency-Track collector unit tests."""

import json
from typing import TYPE_CHECKING

from source_collectors.dependency_track.json_types import (
    DependencyTrackComponent,
    DependencyTrackMetrics,
    DependencyTrackProject,
)

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase

if TYPE_CHECKING:
    from model.measurement import MetricMeasurement


class DependencyTrackTestCase(SourceCollectorTestCase):
    """Base class for Dependency-Track collector unit tests."""

    SOURCE_TYPE = "dependency_track"

    def setUp(self) -> None:
        """Extend to add the mandatory landing URL."""
        super().setUp()
        self.landing_url = f"https://{self.SOURCE_TYPE}/landing"
        self.sources["source_id"]["parameters"]["landing_url"] = self.landing_url

    def projects(self, version: str = "1.4", *, is_latest: bool = False) -> list[DependencyTrackProject]:
        """Create the Dependency-Track projects fixture."""
        project = DependencyTrackProject(
            isLatest=is_latest,
            name="project name",
            uuid="project uuid",
            lastBomImport=0,
            metrics=DependencyTrackMetrics(),
        )
        if version:
            project["version"] = version
        return [project]

    def component(
        self,
        name: str = "component name",
        uuid: str = "component-uuid",
        direct_dependencies: list[str] | None = None,
        project: DependencyTrackProject | None = None,
    ) -> DependencyTrackComponent:
        """Create a Dependency-Track component fixture, with the UUIDs of its direct dependencies, if any."""
        component = DependencyTrackComponent(
            name=name,
            project=self.projects()[0] if project is None else project,
            uuid=uuid,
            version="1.0",
        )
        if direct_dependencies is not None:
            component["directDependencies"] = json.dumps([{"uuid": child} for child in direct_dependencies])
        return component

    def root_component_attributes(self, name: str, uuid: str = "") -> dict[str, str]:
        """Create the expected root component entity attributes. Pass the UUID if a landing URL is expected."""
        attributes = {"root_component": name}
        if uuid:
            attributes["root_component_landing_url"] = f"{self.landing_url}/components/{uuid}"
        return attributes

    def assert_no_projects_found(self, measurement: MetricMeasurement) -> None:
        """Assert that no projects have been found."""
        self.assert_measurement(measurement, connection_error="No projects found")
