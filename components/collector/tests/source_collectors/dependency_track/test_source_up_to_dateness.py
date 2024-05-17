"""Unit tests for the Dependency-Track source up-to-dateness collector."""

from datetime import datetime, timedelta

from dateutil.tz import tzlocal

from source_collectors.dependency_track.base import DependencyTrackProject

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class DependencyTrackSourceUpToDatenessVersionTest(SourceCollectorTestCase):
    """Unit tests for the Dependency-Track source up-to-dateness collector."""

    METRIC_ADDITION = "min"
    METRIC_TYPE = "source_up_to_dateness"
    SOURCE_TYPE = "dependency_track"
    LANDING_URL = "https://dependency_track"

    def projects(self) -> list[DependencyTrackProject]:
        """Create Dependency-Track projects fixture."""
        now = datetime.now(tz=tzlocal()).replace(microsecond=0)
        self.yesterday = now - timedelta(days=1)
        yesterday_timestamp = round(self.yesterday.timestamp() * 1000)
        self.last_week = now - timedelta(days=7)
        last_week_timestamp = round(self.last_week.timestamp() * 1000)
        return [
            DependencyTrackProject(name="Project 1", version="1.1", uuid="p1", lastBomImport=yesterday_timestamp),
            DependencyTrackProject(name="Project 2", version="1.2", uuid="p2", lastBomImport=last_week_timestamp),
        ]

    def entities(self) -> list[dict[str, str]]:
        """Create the expected entities."""
        return [
            {
                "key": "p1",
                "last_bom_import": self.yesterday.isoformat(),
                "project": "Project 1",
                "project_landing_url": "/projects/p1",
            },
            {
                "key": "p2",
                "last_bom_import": self.last_week.isoformat(),
                "project": "Project 2",
                "project_landing_url": "/projects/p2",
            },
        ]

    async def test_source_up_to_dateness(self):
        """Test that the source up-to-dateness can be measured."""
        response = await self.collect(get_request_json_return_value=self.projects())
        self.assert_measurement(response, value="7", landing_url=self.LANDING_URL, entities=self.entities())

    async def test_filter_by_project_name(self):
        """Test that projects can be filtered by name."""
        self.set_source_parameter("project_names", ["other project"])
        response = await self.collect(get_request_json_return_value=self.projects())
        self.assert_measurement(response, parse_error="No projects found")

    async def test_filter_by_regular_expression(self):
        """Test that projects can be filtered by regular expression."""
        self.set_source_parameter("project_names", ["Project .*"])
        response = await self.collect(get_request_json_return_value=self.projects())
        self.assert_measurement(response, value="7", landing_url=self.LANDING_URL, entities=self.entities())

    async def test_filter_by_project_version(self):
        """Test filtering projects by version."""
        self.set_source_parameter("project_versions", ["1.2", "1.3"])
        response = await self.collect(get_request_json_return_value=self.projects())
        self.assert_measurement(response, value="7", landing_url=self.LANDING_URL, entities=self.entities()[1:])

    async def test_filter_by_project_name_and_version(self):
        """Test filtering projects by name and version."""
        self.set_source_parameter("project_names", ["Project .*"])
        self.set_source_parameter("project_versions", ["1.3", "1.4"])
        response = await self.collect(get_request_json_return_value=self.projects())
        self.assert_measurement(response, parse_error="No projects found")
