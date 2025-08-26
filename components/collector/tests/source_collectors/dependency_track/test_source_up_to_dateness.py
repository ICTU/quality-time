"""Unit tests for the Dependency-Track source up-to-dateness collector."""

from datetime import datetime, timedelta

from dateutil.tz import tzlocal

from source_collectors.dependency_track.base import DependencyTrackBase
from source_collectors.dependency_track.json_types import DependencyTrackMetrics, DependencyTrackProject

from .base_test import DependencyTrackTestCase


class DependencyTrackSourceUpToDatenessVersionTest(DependencyTrackTestCase):
    """Unit tests for the Dependency-Track source up-to-dateness collector."""

    METRIC_ADDITION = "min"
    METRIC_TYPE = "source_up_to_dateness"
    LANDING_URL = "https://dependency_track"

    def projects(self, version: str = "1.4") -> list[DependencyTrackProject]:
        """Create Dependency-Track projects fixture."""
        now = datetime.now(tz=tzlocal()).replace(microsecond=0)
        self.yesterday = now - timedelta(days=1)
        yesterday_timestamp = round(self.yesterday.timestamp() * 1000)
        self.day_before_yesterday = now - timedelta(days=2)
        day_before_yesterday_timestamp = round(self.day_before_yesterday.timestamp() * 1000)
        self.last_week = now - timedelta(days=7)
        self.last_week_timestamp = round(self.last_week.timestamp() * 1000)
        self.few_days_ago = now - timedelta(days=4)
        self.few_days_ago_timestamp = round(self.few_days_ago.timestamp() * 1000)
        return [
            DependencyTrackProject(
                isLatest=True,
                name="Project 1",
                version="1.1",
                uuid="p1",
                lastBomImport=yesterday_timestamp,
                metrics=DependencyTrackMetrics(lastOccurrence=self.few_days_ago_timestamp),
            ),
            DependencyTrackProject(
                isLatest=False,
                name="Project 2",
                version="1.2",
                uuid="p2",
                lastBomImport=self.last_week_timestamp,
                metrics=DependencyTrackMetrics(lastOccurrence=day_before_yesterday_timestamp),
            ),
        ]

    def entities(self) -> list[dict[str, str | bool]]:
        """Create the expected entities."""
        return [
            {
                "key": "p1",
                "last_bom_analysis": self.few_days_ago.isoformat(),
                "last_bom_import": self.yesterday.isoformat(),
                "is_latest": "true",
                "project": "Project 1",
                "project_landing_url": "/projects/p1",
                "up_to_date": "yes",
                "version": "1.1",
            },
            {
                "key": "p2",
                "is_latest": "false",
                "last_bom_analysis": self.day_before_yesterday.isoformat(),
                "last_bom_import": self.last_week.isoformat(),
                "project": "Project 2",
                "project_landing_url": "/projects/p2",
                "up_to_date": "nearly",
                "version": "1.2",
            },
        ]

    async def test_source_up_to_dateness(self):
        """Test that the source up-to-dateness can be measured."""
        response = await self.collect(get_request_json_return_value=self.projects())
        self.assert_measurement(response, value="7", landing_url=self.LANDING_URL, entities=self.entities())

    async def test_source_up_to_dateness_missing_bom_analysis(self):
        """Test that the source up-to-dateness can be measured even if the BOM has no last analysis datetime."""
        projects = self.projects()
        projects.append(
            DependencyTrackProject(
                name="Project 3",
                uuid="p3",
                lastBomImport=self.last_week_timestamp,
                isLatest=True,
                metrics=DependencyTrackMetrics(),
                version="1.3",
            )
        )
        entities = self.entities()
        entities.append(
            {
                "key": "p3",
                "last_bom_analysis": "",
                "last_bom_import": self.last_week.isoformat(),
                "is_latest": "true",
                "project": "Project 3",
                "project_landing_url": "/projects/p3",
                "up_to_date": "nearly",
                "version": "1.3",
            }
        )
        response = await self.collect(get_request_json_return_value=projects)
        self.assert_measurement(response, value="7", landing_url=self.LANDING_URL, entities=entities)

    async def test_source_up_to_dateness_missing_bom_import(self):
        """Test that the source up-to-dateness can be measured even if the BOM has no import datetime."""
        projects = self.projects()
        projects.append(
            DependencyTrackProject(
                name="Project 3",
                version="1.3",
                uuid="p3",
            )
        )
        entities = self.entities()
        entities.append(
            {
                "key": "p3",
                "last_bom_analysis": "",
                "last_bom_import": "",
                "is_latest": "false",
                "project": "Project 3",
                "project_landing_url": "/projects/p3",
                "up_to_date": "unknown",
                "version": "1.3",
            }
        )
        response = await self.collect(get_request_json_return_value=projects)
        self.assert_measurement(response, value="7", landing_url=self.LANDING_URL, entities=entities)

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

    async def test_filter_by_event_type_last_bom_import(self):
        """Test that projects can be filtered by event type."""
        self.set_source_parameter("project_event_types", ["last BOM import"])
        response = await self.collect(get_request_json_return_value=self.projects())
        self.assert_measurement(response, value="7", landing_url=self.LANDING_URL, entities=self.entities())

    async def test_filter_by_event_type_last_bom_analysis(self):
        """Test that projects can be filtered by event type."""
        self.set_source_parameter("project_event_types", ["last BOM analysis"])
        response = await self.collect(get_request_json_return_value=self.projects())
        entities = self.entities()
        entities[0]["up_to_date"] = "nearly"
        entities[1]["up_to_date"] = "yes"
        self.assert_measurement(response, value="4", landing_url=self.LANDING_URL, entities=entities)

    async def test_filter_by_latest_project(self):
        """Test that projects can be filtered by being the latest project version."""
        self.set_source_parameter("only_include_latest_project_versions", "yes")
        response = await self.collect(get_request_json_return_value=self.projects())
        self.assert_measurement(response, value="1", landing_url=self.LANDING_URL, entities=self.entities()[:1])

    async def test_source_up_to_dateness_with_pagination(self):
        """Test that the source up-to-dateness can be measured when pagination is needed."""
        default_size = DependencyTrackBase.PAGE_SIZE
        DependencyTrackBase.PAGE_SIZE = 1
        response = await self.collect(get_request_json_return_value=self.projects())
        self.assert_measurement(response, value="7", landing_url=self.LANDING_URL, entities=self.entities())
        DependencyTrackBase.PAGE_SIZE = default_size

    async def test_source_up_to_dateness_with_reversed_direction(self):
        """Test that the source up-to-dateness can be measured if the metric direction has been reversed."""
        self.metric["direction"] = ">"
        response = await self.collect(get_request_json_return_value=self.projects())
        entities = self.entities()
        entities[0]["up_to_date"] = "no"
        entities[1]["up_to_date"] = "yes"
        self.assert_measurement(response, value="1", landing_url=self.LANDING_URL, entities=entities)
