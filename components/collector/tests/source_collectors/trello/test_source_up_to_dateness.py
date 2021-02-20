"""Unit tests for the Trello source up-to-dateness collector."""

from datetime import datetime

from .base import TrelloTestCase


class TrelloSourceUpToDatenessTest(TrelloTestCase):
    """Unit tests for the Trello source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    async def test_age(self):
        """Test that the source up to dateness is the number of days since the most recent change."""
        response = await self.collect(get_request_json_side_effect=self.json)
        self.assert_measurement(response, value=str((datetime.now() - datetime(2019, 3, 3)).days))

    async def test_age_with_ignored_lists(self):
        """Test that lists can be ignored when measuring the source up to dateness."""
        self.set_source_parameter("lists_to_ignore", ["list1"])
        response = await self.collect(get_request_json_side_effect=self.json)
        self.assert_measurement(response, value=str((datetime.now() - datetime(2019, 2, 10)).days))
