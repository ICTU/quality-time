"""Base classes for Gatling collectors."""

from base_collectors import JSONFileSourceCollector, SourceCollector
from collector_utilities.type import URL


class GatlingJSONCollector(JSONFileSourceCollector):
    """Base class for Gatling collectors that read the stats.json file."""

    async def _api_url(self) -> URL:
        """Extend to translate the HTML URL into a URL to the stats.json file."""
        api_url = await super()._api_url()
        api_url.removesuffix("/index.html")
        return URL(api_url + "/js/stats.json")


class GatlingLogCollector(SourceCollector):
    """Base class for Gatling collectors that read the simulation.log file."""

    async def _api_url(self) -> URL:
        """Extend to translate the HTML URL into a URL to the simulation.log file."""
        api_url = await super()._api_url()
        api_url.removesuffix("/index.html")
        return URL(api_url + "/simulation.log")
