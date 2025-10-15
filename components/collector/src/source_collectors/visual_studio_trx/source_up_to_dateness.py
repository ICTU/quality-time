"""Visual Studio TRX source up-to-dateness collector."""

from typing import TYPE_CHECKING

from shared.utils.date_time import now

from base_collectors import TimePassedCollector, XMLFileSourceCollector
from collector_utilities.date_time import parse_datetime
from collector_utilities.functions import parse_source_response_xml_with_namespace

if TYPE_CHECKING:
    from datetime import datetime

    from collector_utilities.type import Response


class VisualStudioTRXSourceUpToDateness(XMLFileSourceCollector, TimePassedCollector):
    """Collector to collect the Visual Studio TRX report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the timestamp from the response."""
        tree, namespaces = await parse_source_response_xml_with_namespace(response)
        times = tree.find("./ns:Times", namespaces)
        return (
            now() if times is None else parse_datetime(times.attrib["creation"])
        )  # The creation attribute is required
