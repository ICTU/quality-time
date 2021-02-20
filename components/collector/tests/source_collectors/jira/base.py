"""Unit tests for the Jira metric source."""

from ..source_collector_test_case import SourceCollectorTestCase


class JiraTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Base class for Jira unit tests."""

    SOURCE_TYPE = "jira"

    def setUp(self):
        """Extend to create sources and a metric of type METRIC_TYPE."""
        super().setUp()
        self.url = "https://jira"
        parameters = self.sources["source_id"]["parameters"]
        parameters["story_points_field"] = "field"
        parameters["manual_test_execution_frequency_field"] = "desired_test_frequency"
        parameters["manual_test_duration_field"] = "field"
        parameters["board"] = "Board 2"
        self.created = "2020-08-06T16:36:48.000+0200"

    def issue(self, key="1", **fields):
        """Create a Jira issue."""
        return dict(id=key, key=key, fields=dict(created=self.created, summary=f"Summary {key}", **fields))

    def entity(self, key="1", created=None, updated=None, issuetype="Unknown issue type", **kwargs):
        """Create an entity."""
        return dict(
            key=key,
            summary=f"Summary {key}",
            url=f"{self.url}/browse/{key}",
            created=created or self.created,
            updated=updated,
            status=None,
            priority=None,
            type=issuetype,
            **kwargs,
        )

    async def get_response(self, issues_json, fields_json=None):
        """Get the collector's response."""
        return await self.collect(self.metric, get_request_json_side_effect=[fields_json or [], issues_json])
