"""Cobertura coverage report source up-to-dateness collector."""

from typing import TYPE_CHECKING

from base_collectors import TimePassedCollector, XMLFileSourceCollector
from collector_utilities.date_time import datetime_from_timestamp
from collector_utilities.exceptions import NotFoundError
from collector_utilities.functions import parse_source_response_xml

if TYPE_CHECKING:
    from datetime import datetime

    from collector_utilities.type import Response


class CoberturaSourceUpToDateness(XMLFileSourceCollector, TimePassedCollector):
    """Collector to collect the Cobertura report age."""

    CUTOFF_YEAR_FOR_TIMESTAMP = 1980

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the timestamp from the response."""
        tree = await parse_source_response_xml(response)
        if timestamp := tree.get("timestamp"):
            dt = datetime_from_timestamp(float(timestamp))
            return dt if dt.year > self.CUTOFF_YEAR_FOR_TIMESTAMP else datetime_from_timestamp(float(timestamp) * 1000)
        raise NotFoundError(type_of_thing="Cobertura XML tag", name_of_thing="timestamp")
