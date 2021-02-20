"""Unit tests for the Wekan issues collector."""

from datetime import datetime

from .base import WekanTestCase


class WekanIssuesTest(WekanTestCase):
    """Unit tests for the Wekan issues collector."""

    METRIC_TYPE = "issues"

    async def test_issues(self):
        """Test that the number of issues and the individual issues are returned and that archived cards are ignored."""
        self.json[5]["archived"] = True
        response = await self.collect(self.metric)
        self.assert_measurement(response, value="2", entities=self.entities)

    async def test_issues_with_ignored_list(self):
        """Test that lists can be ignored when counting issues."""
        self.sources["source_id"]["parameters"]["lists_to_ignore"] = ["list2"]
        self.json[5]["archived"] = True
        del self.entities[1]
        response = await self.collect(self.metric)
        self.assert_measurement(response, value="1", entities=self.entities)

    async def test_overdue_issues(self):
        """Test overdue issues."""
        self.sources["source_id"]["parameters"]["cards_to_count"] = ["overdue"]
        self.entities[0]["due_date"] = self.json[4]["dueAt"] = "2019-01-01"
        self.entities[1]["due_date"] = self.json[7]["dueAt"] = "2019-02-02"
        response = await self.collect(self.metric)
        self.assert_measurement(response, value="2", entities=self.entities)

    async def test_inactive_issues(self):
        """Test inactive issues."""
        self.sources["source_id"]["parameters"]["cards_to_count"] = ["inactive"]
        self.json[5]["dateLastActivity"] = datetime.now().isoformat()
        response = await self.collect(self.metric)
        self.assert_measurement(response, value="2", entities=self.entities)
