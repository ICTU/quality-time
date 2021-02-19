"""OpenVAS source up-to-dateness collector."""

from datetime import datetime

from dateutil.parser import isoparse

from base_collectors import SourceUpToDatenessCollector, XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml
from collector_utilities.type import Response


class OpenVASSourceUpToDateness(XMLFileSourceCollector, SourceUpToDatenessCollector):
    """Collector to collect the OpenVAS report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the date and time from the OpenVAS XML."""
        tree = await parse_source_response_xml(response)
        return isoparse(tree.findtext("creation_time", default=""))
