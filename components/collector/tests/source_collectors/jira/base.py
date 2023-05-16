"""Unit tests for the Jira metric source."""

from unittest.mock import patch

from source_collectors.jira.issues import JiraIssues
from ..source_collector_test_case import SourceCollectorTestCase


class JiraTestCase(SourceCollectorTestCase):
    """Base class for Jira unit tests."""

    SOURCE_TYPE = "jira"

    def setUp(self):
        """Extend to create sources and a metric of type METRIC_TYPE."""
        super().setUp()
        self.url = "https://jira"
        self.set_source_parameter("jql", "project = abc")
        self.set_source_parameter("story_points_field", "field")
        self.set_source_parameter("manual_test_duration_field", "field")
        self.set_source_parameter("board", "Board 2")
        self.created = "2020-08-06T16:36:48.000+0200"

    def issue(self, key="1", **fields):
        """Create a Jira issue."""
        return dict(id=key, key=key, fields=dict(created=self.created, summary=f"Summary {key}", **fields))

    def entity(self, key="1", created=None, updated=None, issuetype="Unknown issue type", **kwargs):
        """Create an entity."""
        return dict(
            key=key,
            issue_key=key,
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
        with patch.object(JiraIssues, "max_results", 50):
            return await self.collect(
                get_request_json_side_effect=[fields_json or [dict(id="field", name="Field")], issues_json, issues_json]
            )
