"""Unit tests for the Azure DevOps Server average issue lead time collector."""

from copy import deepcopy
from datetime import datetime, timedelta, UTC

from .base import AzureDevopsTestCase


class AzureDevopsAverageIssueLeadTimeTest(AzureDevopsTestCase):
    """Unit tests for the Azure DevOps Server average issue lead time metric."""

    METRIC_TYPE = "average_issue_lead_time"

    def setUp(self):
        """Extend to add Azure DevOps average issue lead time fixtures."""
        super().setUp()

        now_dt = datetime.now(tz=UTC)
        now_timestamp = now_dt.isoformat()
        yesterday_timestamp = (now_dt - timedelta(days=1)).isoformat()
        last_week_timestamp = (now_dt - timedelta(weeks=1)).isoformat()

        self.work_item1 = deepcopy(self.work_item)
        self.work_item1["id"] = "id1"
        self.work_item1["fields"]["System.State"] = "Done"
        self.work_item1["fields"]["System.CreatedDate"] = yesterday_timestamp
        self.work_item1["fields"]["System.ChangedDate"] = now_timestamp  # NOSONAR

        self.work_item2 = deepcopy(self.work_item)
        self.work_item2["id"] = "id2"
        self.work_item2["fields"]["System.State"] = "Done"
        self.work_item2["fields"]["System.CreatedDate"] = last_week_timestamp
        self.work_item2["fields"]["System.ChangedDate"] = now_timestamp  # NOSONAR

        self.expected_entities = [
            {
                "key": "id1",
                "project": "Project",
                "title": "Title",
                "work_item_type": "Task",
                "state": "Done",
                "url": self.work_item_url,
                "lead_time": 1,
                "changed_field": now_timestamp,
            },
            {
                "key": "id2",
                "project": "Project",
                "title": "Title",
                "work_item_type": "Task",
                "state": "Done",
                "url": self.work_item_url,
                "lead_time": 7,
                "changed_field": now_timestamp,
            },
        ]

    async def test_lead_time(self):
        """Test that the lead time is returned."""
        response = await self.collect(
            post_request_json_side_effect=[
                {"workItems": [{"id": "id"}, {"id": "id1"}, {"id": "id2"}]},
                {"value": [self.work_item, self.work_item1, self.work_item2]},
            ],
        )
        self.assert_measurement(response, value="4", entities=self.expected_entities)  # 7 + 1 / 2

    async def test_lead_time_without_stories(self):
        """Test that the lead time is zero when there are no work items."""
        response = await self.collect(post_request_json_return_value={"workItems": []})
        self.assert_measurement(response, value="0", entities=[])

    async def test_lead_time_without_changed_date(self):
        """Test that the lead time is zero when there are no work items with changed date."""
        self.work_item2["fields"]["System.ChangedDate"] = None
        response = await self.collect(
            post_request_json_side_effect=[{"workItems": [{"id": "id"}]}, {"value": [self.work_item2]}],
        )
        self.assert_measurement(response, value="0", entities=[])
