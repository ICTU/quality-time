"""JUnit time passed collector."""

from datetime import datetime

from dateutil.parser import parse

from base_collectors import TimePassedCollector, XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml
from collector_utilities.type import Response


class JUnitTimePassed(XMLFileSourceCollector, TimePassedCollector):
    """Collector to collect the Junit report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the timestamp from the response."""
        tree = await parse_source_response_xml(response)
        test_suites = [tree] if tree.tag == "testsuite" else tree.findall("testsuite")
        # If <testsuites> has at least one <testsuite> get the timestamp from the first <testsuite>. Since we're only
        # interested in the date that the test ran, and not the exact time, we're assuming we don't need to look for
        # the oldest testsuite. If there's no <testsuite> within the <testsuites>, we can't get a timestamp and return
        # datetime.now(). We don't return datetime.min because there might be more Junit XML files being parsed that do
        # have a timestamp. If we'd return datetime.min, TimePassedCollector._parse_source_responses() would
        # always return datetime.min as it returns the oldest timestamp it sees.
        return parse(test_suites[0].get("timestamp", "")) if test_suites else datetime.now()
