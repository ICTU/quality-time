"""Unit tests for the Azure DevOps Server lead time for changes collector."""

from copy import deepcopy
from datetime import datetime, timedelta

from .base import AzureDevopsTestCase


class AzureDevopsLeadTimeForChangesTest(AzureDevopsTestCase):
    """Unit tests for the Azure DevOps Server lead time for changes metric."""

    METRIC_TYPE = "lead_time_for_changes"

    def setUp(self):
        """Extend to add Azure DevOps lead time for changes fixtures."""
        super().setUp()

        now_dt = datetime.now()
        now_timestamp = now_dt.isoformat()
        yesterday_timestamp = (now_dt - timedelta(days=1)).isoformat()
        last_week_timestamp = (now_dt - timedelta(weeks=1)).isoformat()

        self.work_item1 = deepcopy(self.work_item)
        self.work_item1["fields"]["System.State"] = "Done"
        self.work_item1["fields"]["System.CreatedDate"] = yesterday_timestamp
        self.work_item1["fields"]["System.ChangedDate"] = now_timestamp  # NOSONAR

        self.work_item2 = deepcopy(self.work_item)
        self.work_item2["fields"]["System.State"] = "Done"
        self.work_item2["fields"]["System.CreatedDate"] = last_week_timestamp
        self.work_item2["fields"]["System.ChangedDate"] = now_timestamp  # NOSONAR

    async def test_lead_time(self):
        """Test that the lead time is returned."""
        response = await self.collect(post_request_json_side_effect=[
            dict(workItems=[dict(id="id"), dict(id="id1"), dict(id="id2")]),
            dict(value=[self.work_item, self.work_item1, self.work_item2])
        ])
        self.assert_measurement(response, value="4")  # 7 + 1 / 2

    async def test_lead_time_without_stories(self):
        """Test that the lead time is zero when there are no work items."""
        response = await self.collect(post_request_json_return_value=dict(workItems=[]))
        self.assert_measurement(response, value="0", entities=[])

    async def test_lead_time_without_changed_date(self):
        """Test that the lead time is zero when there are no work items with changed date."""
        self.work_item2["fields"]["System.ChangedDate"] = None
        response = await self.collect(post_request_json_side_effect=[
            dict(workItems=[dict(id="id")]),
            dict(value=[self.work_item2])
        ])
        self.assert_measurement(response, value="0", entities=[])
