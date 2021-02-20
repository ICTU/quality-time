"""axe-selenium-python accessibility source up-to-dateness collector."""

from datetime import datetime

from dateutil.parser import parse

from base_collectors import JSONFileSourceCollector, SourceUpToDatenessCollector
from collector_utilities.type import Response


class AxeSeleniumPythonSourceUpToDateness(JSONFileSourceCollector, SourceUpToDatenessCollector):
    """Collector to get the source up-to-dateness of axe-selenium-python JSON reports."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the timestamp from the response."""
        return parse((await response.json(content_type=None))["timestamp"])
