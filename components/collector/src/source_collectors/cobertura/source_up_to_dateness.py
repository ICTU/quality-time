"""Cobertura coverage report source up-to-dateness collector."""

from datetime import datetime

from base_collectors import SourceUpToDatenessCollector, XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml
from collector_utilities.type import Response


class CoberturaSourceUpToDateness(XMLFileSourceCollector, SourceUpToDatenessCollector):
    """Collector to collect the Cobertura report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the timestamp from the response."""
        tree = await parse_source_response_xml(response)
        return datetime.utcfromtimestamp(int(tree.get("timestamp", 0)) / 1000.0)
