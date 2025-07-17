"""Base classes for Dependency-Track collector unit tests."""

from typing import TYPE_CHECKING

from source_collectors.dependency_track.json_types import DependencyTrackMetrics, DependencyTrackProject

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
        self.sources["source_id"]["parameters"]["landing_url"] = self.landing_url  # type: ignore[index]

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

    def assert_no_projects_found(self, measurement: MetricMeasurement) -> None:
        """Assert that no projects have been found."""
        self.assert_measurement(measurement, connection_error="No projects found")
