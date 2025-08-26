"""Base classes for Dependency-Track collector unit tests."""

from source_collectors.dependency_track.json_types import DependencyTrackMetrics, DependencyTrackProject

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class DependencyTrackTestCase(SourceCollectorTestCase):
    """Base class for Dependency-Track collector Unit tests."""

    SOURCE_TYPE = "dependency_track"

    def projects(self, version: str = "1.4") -> list[DependencyTrackProject]:
        """Create the Dependency-Track projects fixture."""
        project = DependencyTrackProject(
            isLatest=False,
            name="project name",
            uuid="project uuid",
            lastBomImport=0,
            metrics=DependencyTrackMetrics(),
        )
        if version:
            project["version"] = version
        return [project]
