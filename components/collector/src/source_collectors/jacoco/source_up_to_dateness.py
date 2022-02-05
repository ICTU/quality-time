"""Jacoco coverage report source up-to-dateness collector."""

from datetime import datetime

from base_collectors import TimePassedCollector, XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml
from collector_utilities.type import Response


class JacocoSourceUpToDateness(XMLFileSourceCollector, TimePassedCollector):
    """Collector to collect the Jacoco report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the datetime from the JaCoCo XML."""
        tree = await parse_source_response_xml(response)
        session_info = tree.find(".//sessioninfo")
        timestamp = session_info.get("dump", 0) if session_info is not None else 0
        return datetime.utcfromtimestamp(int(timestamp) / 1000.0)
