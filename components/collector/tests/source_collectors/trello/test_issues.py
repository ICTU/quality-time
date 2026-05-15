"""Unit tests for the Trello issues collector."""

from shared.utils.functions import iso_timestamp

from .base import TrelloTestCase


class TrelloIssuesTest(TrelloTestCase):
    """Unit tests for the Trello issues collector."""

    METRIC_TYPE = "issues"

    async def test_issues(self):
        """Test that the number of issues and the individual issues are returned."""
        measurement = await self.collect_measurement(get_request_json_side_effect=self.json)
        self.assert_measurement(measurement, value="2", entities=self.entities)

    async def test_issues_with_ignored_list(self):
        """Test that lists can be ignored when counting issues."""
        self.set_source_parameter("lists_to_ignore", ["list1"])
        measurement = await self.collect_measurement(get_request_json_side_effect=self.json)
        self.assert_measurement(measurement, value="1", entities=[self.entities[1]])

    async def test_overdue_issues(self):
        """Test overdue issues; when the parameter is set, only count this type."""
        self.set_source_parameter("cards_to_count", ["overdue"])
        measurement = await self.collect_measurement(get_request_json_side_effect=self.json)
        self.assert_measurement(measurement, value="1", entities=[self.entities[1]])

    async def test_inactive_issues(self):
        """Test inactive issues; when the parameter is set, only count this type."""
        self.set_source_parameter("cards_to_count", ["inactive"])
        self.cards["cards"][0]["dateLastActivity"] = iso_timestamp()
        measurement = await self.collect_measurement(get_request_json_side_effect=self.json)
        self.assert_measurement(measurement, value="1", entities=[self.entities[1]])
