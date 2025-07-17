"""Jacoco coverage report source up-to-dateness collector."""

from typing import TYPE_CHECKING

from base_collectors import TimePassedCollector, XMLFileSourceCollector
from collector_utilities.date_time import datetime_from_timestamp
from collector_utilities.functions import parse_source_response_xml

if TYPE_CHECKING:
    from datetime import datetime

    from collector_utilities.type import Response


class JacocoSourceUpToDateness(XMLFileSourceCollector, TimePassedCollector):
    """Collector to collect the Jacoco report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the datetime from the JaCoCo XML."""
        tree = await parse_source_response_xml(response)
        session_info = tree.find(".//sessioninfo")
        timestamp = session_info.get("dump", 0) if session_info is not None else 0
        return datetime_from_timestamp(int(timestamp))
