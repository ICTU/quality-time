"""Wekan source up-to-dateness collector."""

from dateutil.parser import parse

from collector_utilities.functions import days_ago
from collector_utilities.type import Value
from source_model import SourceResponses

from .base import WekanBase


class WekanSourceUpToDateness(WekanBase):
    """Collector to measure how up-to-date a Wekan board is."""

    async def _parse_value(self, responses: SourceResponses) -> Value:
        """Override to parse the date and time of the most recent activity from the cards and lists."""
        dates = [self._board.get("createdAt"), self._board.get("modifiedAt")]
        for lst in self._lists:
            dates.extend([lst.get("createdAt"), lst.get("updatedAt")])
            dates.extend([card["dateLastActivity"] for card in self._cards.get(lst["_id"], [])])
        return str(days_ago(parse(max([date for date in dates if date]))))
