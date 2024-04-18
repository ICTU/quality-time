"""NCover source up-to-dateness collector."""

import re
from datetime import datetime

from base_collectors import TimePassedCollector
from collector_utilities.date_time import datetime_from_timestamp
from collector_utilities.type import Response

from .base import NCoverBase


class NCoverSourceUpToDateness(NCoverBase, TimePassedCollector):
    """Collector to collect the NCover report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the date and time from the NCover HTML/JavaScript."""
        script = await self._find_script(response, "ncover.createDateTime")
        match = re.search(r"ncover\.createDateTime = '(\d+)'", script)
        timestamp = match.group(1) if match else ""
        return datetime_from_timestamp(float(timestamp))
