"""Unit tests for the Dependency-Track source up-to-dateness collector."""

from datetime import datetime, timedelta

from dateutil.tz import tzlocal

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class DependencyTrackSourceUpToDatenessVersionTest(SourceCollectorTestCase):
    """Unit tests for the Dependency-Track source up-to-dateness collector."""

    METRIC_ADDITION = "min"
    METRIC_TYPE = "source_up_to_dateness"
    SOURCE_TYPE = "dependency_track"

    async def test_source_up_to_dateness(self):
        """Test that the source up-to-dateness can be measured."""
        now = datetime.now(tz=tzlocal()).replace(microsecond=0)
        yesterday = now - timedelta(days=1)
        yesterday_timestamp = yesterday.timestamp() * 1000  # To be prepared, test a timestamp that is a float...
        last_week = now - timedelta(days=7)
        last_week_timestamp = str(int(last_week.timestamp() * 1000))  # ... and test a string containing an integer
        projects = [
            {"name": "Project 1", "lastBomImport": yesterday_timestamp, "uuid": "p1"},
            {"name": "Project 2", "lastBomImport": str(int(last_week_timestamp)), "uuid": "p2"},
        ]
        response = await self.collect(get_request_json_return_value=projects)
        self.assert_measurement(
            response,
            value="7",
            landing_url="https://dependency_track",
            entities=[
                {
                    "key": "p1",
                    "last_bom_import": yesterday.isoformat(),
                    "project": "Project 1",
                    "project_landing_url": "/projects/p1",
                },
                {
                    "key": "p2",
                    "last_bom_import": last_week.isoformat(),
                    "project": "Project 2",
                    "project_landing_url": "/projects/p2",
                },
            ],
        )
