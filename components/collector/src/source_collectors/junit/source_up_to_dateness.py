"""JUnit metric collector."""

from datetime import datetime

from dateutil.parser import parse

from base_collectors import SourceUpToDatenessCollector, XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml
from collector_utilities.type import Response


class JUnitSourceUpToDateness(XMLFileSourceCollector, SourceUpToDatenessCollector):
    """Collector to collect the Junit report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the timestamp from the response."""
        tree = await parse_source_response_xml(response)
        test_suite = tree if tree.tag == "testsuite" else tree.findall("testsuite")[0]
        return parse(test_suite.get("timestamp", ""))
