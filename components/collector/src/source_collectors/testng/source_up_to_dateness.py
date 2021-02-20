"""TestNG source up-to-dateness collector."""

from datetime import datetime

from dateutil.parser import parse

from base_collectors import SourceUpToDatenessCollector, XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml
from collector_utilities.type import Response


class TestNGSourceUpToDateness(XMLFileSourceCollector, SourceUpToDatenessCollector):
    """Collector to collect the TestNG report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the date and time from the TesTNG XML."""
        tree = await parse_source_response_xml(response)
        test_suite = tree.findall("suite")[0]
        return parse(test_suite.get("finished-at") or "")
