"""Calendar time remaining collector."""

from typing import TYPE_CHECKING, cast

from base_collectors import TimeRemainingCollector
from collector_utilities.date_time import MIN_DATETIME, parse_datetime

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime

    from collector_utilities.type import Response
    from model import SourceResponses


class CalendarTimeRemaining(TimeRemainingCollector):
    """Collector class to get the number of days remaining until a user-specified date."""

    async def _parse_source_response_date_times(self, responses: SourceResponses) -> Sequence[datetime]:
        """Override to return the date from the user-supplied date parameter."""
        return [parse_datetime(cast(str, self._parameter("date")))]

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to document that this method is never called.

        Since the Calendar has no real source responses, we return the answer in _parse_source_response_date_times()
        and this method is never called.
        """
        return MIN_DATETIME  # pragma: no cover
