"""Base classes for Gatling collectors."""

import re

from base_collectors import JSONFileSourceCollector, SourceCollector
from collector_utilities.type import URL
from model import SourceResponses


class GatlingCollector(SourceCollector):
    """Base class for Gatling collectors."""

    INDEX_HTML = "/index.html"
    FILEPATH = "subclass responsibility"

    async def _api_url(self) -> URL:
        """Extend to translate the HTML URL into a URL to the Gatling file that the collector needs."""
        api_url = await super()._api_url()
        if api_url.endswith(self.INDEX_HTML):
            return URL(api_url.removesuffix(self.INDEX_HTML) + self.FILEPATH)
        return api_url


class GatlingJSONCollector(JSONFileSourceCollector, GatlingCollector):
    """Base class for Gatling collectors that read the stats.json file."""

    FILEPATH = "/js/stats.json"


class GatlingLogCollector(GatlingCollector):
    """Base class for Gatling collectors that read the simulation.log file."""

    FILEPATH = "/simulation.log"

    @classmethod
    async def _timestamps(cls, responses: SourceResponses) -> set[int]:
        """Return the timestamps in the simulation.log."""
        timestamps = set()
        for response in responses:
            text = await response.text()
            timestamps |= {int(timestamp) for timestamp in re.findall(r"\d{13}", text)}
        return timestamps
