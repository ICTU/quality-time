"""Calendar metric source."""

from datetime import datetime
from typing import cast

from collector_utilities.functions import days_ago
from collector_utilities.type import Responses, Value
from .source_collector import LocalSourceCollector


class CalendarSourceUpToDateness(LocalSourceCollector):
    """Collector class to get the number of days since a user-specified date."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(days_ago(datetime.fromisoformat(cast(str, self._parameter("date")))))
