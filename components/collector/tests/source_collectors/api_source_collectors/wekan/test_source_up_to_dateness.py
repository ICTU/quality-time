"""Unit tests for the Wekan source up-to-dateness collector."""

from datetime import datetime

from .base import WekanTestCase


class WekanSourceUpToDatenessTest(WekanTestCase):
    """Unit tests for the Wekan source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    async def test_age_with_ignored_lists(self):
        """Test that lists can be ignored when measuring the number of days since the last activity."""
        self.sources["source_id"]["parameters"]["lists_to_ignore"] = ["list1"]
        response = await self.collect(self.metric)
        self.assert_measurement(response, value=str((datetime.now() - datetime(2019, 1, 1)).days))
