"""Calendar time remaining collector."""

from collections.abc import Sequence
from datetime import datetime
from typing import cast

from base_collectors import TimeRemainingCollector
from collector_utilities.type import Response
from model import SourceResponses


class CalendarTimeRemaining(TimeRemainingCollector):
    """Collector class to get the time remaining until a user-specified date."""

    async def _parse_source_response_date_times(self, responses: SourceResponses) -> Sequence[datetime]:
        """Override to return the date from the user-supplied date parameter."""
        return [datetime.fromisoformat(cast(str, self._parameter("date")))]

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to document that this method is never called.

        Since the Calendar has no real source responses, we return the answer in _parse_source_response_date_times()
        and this method is never called.
        """
