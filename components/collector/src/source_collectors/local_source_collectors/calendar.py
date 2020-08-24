"""Calendar metric source."""

from datetime import datetime
from typing import Sequence, cast

from base_collectors import SourceResponses, SourceUpToDatenessCollector
from collector_utilities.type import Response


class CalendarSourceUpToDateness(SourceUpToDatenessCollector):
    """Collector class to get the number of days since a user-specified date."""

    async def _parse_source_response_date_times(self, responses: SourceResponses) -> Sequence[datetime]:
        return [datetime.fromisoformat(cast(str, self._parameter("date")))]

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        # Since the Calendar has no real source responses, we return the answer in _parse_source_response_date_times()
        # and this method is never called
        pass  # pragma: no cover
