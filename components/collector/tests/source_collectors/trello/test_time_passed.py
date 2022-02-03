"""Unit tests for the Trello time passed collector."""

from datetime import datetime

from .base import TrelloTestCase


class TrelloTimePassedTest(TrelloTestCase):
    """Unit tests for the Trello time passed collector."""

    METRIC_TYPE = "time_passed"
    METRIC_ADDITION = "max"

    async def test_age(self):
        """Test that the time passed is the number of days since the most recent change."""
        response = await self.collect(get_request_json_side_effect=self.json)
        self.assert_measurement(response, value=str((datetime.now() - datetime(2019, 3, 3)).days))

    async def test_age_with_ignored_lists(self):
        """Test that lists can be ignored when measuring the time passed."""
        self.set_source_parameter("lists_to_ignore", ["list1"])
        response = await self.collect(get_request_json_side_effect=self.json)
        self.assert_measurement(response, value=str((datetime.now() - datetime(2019, 2, 10)).days))
