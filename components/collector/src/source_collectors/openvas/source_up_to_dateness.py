"""OpenVAS source up-to-dateness collector."""

from datetime import datetime

from base_collectors import TimePassedCollector, XMLFileSourceCollector
from collector_utilities.date_time import parse_datetime
from collector_utilities.functions import parse_source_response_xml
from collector_utilities.type import Response


class OpenVASSourceUpToDateness(XMLFileSourceCollector, TimePassedCollector):
    """Collector to collect the OpenVAS report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the date and time from the OpenVAS XML."""
        tree = await parse_source_response_xml(response)
        return parse_datetime(tree.findtext("creation_time", default=""))
