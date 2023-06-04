"""Robot Framework source up-to-dateness collector."""

from datetime import datetime

from base_collectors import TimePassedCollector
from collector_utilities.date_time import parse_datetime
from collector_utilities.functions import parse_source_response_xml
from collector_utilities.type import Response

from .base import RobotFrameworkBaseClass


class RobotFrameworkSourceUpToDateness(RobotFrameworkBaseClass, TimePassedCollector):
    """Collector to collect the Robot Framework report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the date and time from the Robot Framework XML."""
        return parse_datetime((await parse_source_response_xml(response)).get("generated", ""))
