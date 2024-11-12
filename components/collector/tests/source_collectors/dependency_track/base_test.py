"""Base classes for Dependency-Track collector unit tests."""

from source_collectors.dependency_track.base import DependencyTrackMetrics, DependencyTrackProject

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class DependencyTrackTestCase(SourceCollectorTestCase):
    """Base class for Dependency-Track collector Unit tests."""

    SOURCE_TYPE = "dependency_track"

    def projects(self) -> list[DependencyTrackProject]:
        """Create the Dependency-Track projects fixture."""
        return [
            DependencyTrackProject(
                name="project name",
                uuid="project uuid",
                version="1.4",
                lastBomImport=0,
                metrics=DependencyTrackMetrics(),
            ),
        ]
