"""JUnit metric collector."""

from typing import TYPE_CHECKING

from shared.utils.date_time import now

from base_collectors import TimePassedCollector, XMLFileSourceCollector
from collector_utilities.date_time import parse_datetime
from collector_utilities.functions import parse_source_response_xml

if TYPE_CHECKING:
    from datetime import datetime
    from xml.etree.ElementTree import Element  # nosec # Element is not available from defusedxml, but only used as type

    from collector_utilities.type import Response


class JUnitSourceUpToDateness(XMLFileSourceCollector, TimePassedCollector):
    """Collector to collect the Junit report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the timestamp from the response."""
        # Check if root element has a timestamp (either <testsuites> or <testsuite>) and use that. Since we're only
        # interested in the date that the test ran, and not the exact time, we're assuming we don't need to look for
        # the oldest testsuite.
        tree = await parse_source_response_xml(response)
        if timestamp := self._get_timestamp(tree):
            return timestamp

        # If there is no timestamp on the root we use the first <testsuite> we can find with a timestamp.
        if timestamp := next(filter(bool, (self._get_timestamp(el) for el in tree.findall("testsuite"))), None):
            return timestamp

        # If there's no suitable <testsuite> within the <testsuites>, we can't get a timestamp and return
        # datetime.now(). We don't return datetime.min because there might be more Junit XML files being parsed that do
        # have a timestamp. If we'd return datetime.min, SourceUpToDatenessCollector._parse_source_responses() would
        # always return datetime.min as it returns the oldest timestamp it sees.
        return now()

    @staticmethod
    def _get_timestamp(element: Element) -> datetime | None:
        if ts := element.get("timestamp"):
            return parse_datetime(ts)
        return None
