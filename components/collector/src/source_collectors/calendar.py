"""Calendar metric source."""

from datetime import datetime
from typing import cast

from collector_utilities.type import Response
from .source_collector import LocalSourceCollector, SourceUpToDatenessCollector


class CalendarSourceUpToDateness(SourceUpToDatenessCollector, LocalSourceCollector):
    """Collector class to get the number of days since a user-specified date."""

    def _parse_source_response_date_time(self, response: Response) -> datetime:
        return datetime.fromisoformat(cast(str, self._parameter("date")))
