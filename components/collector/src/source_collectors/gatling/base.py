"""Base classes for Gatling collectors."""

from abc import ABC
from typing import cast

from bs4 import Tag

from base_collectors import HTMLFileSourceCollector
from collector_utilities.type import URL, Response


class GatlingHTMLCollector(HTMLFileSourceCollector, ABC):
    """Base class for Gatling HTML collectors."""

    INDEX_HTML = "/index.html"

    async def _api_url(self) -> URL:
        """Extend to translate the HTML URL into a URL that the collector needs."""
        api_url = await super()._api_url()
        return api_url if api_url.endswith(self.INDEX_HTML) else URL(api_url + self.INDEX_HTML)

    async def simulation_information(self, response: Response, label: str) -> str:
        """Return the simulation information labeled with the label."""
        soup = await self._soup(response)
        label_span = soup.find("span", {"class": "simulation-information-label"}, string=f"{label}: ")
        if label_span and (parent := label_span.parent):
            return str(parent.find_all("span")[1].get_text())  # The second span contains the information
        return ""

    def get_column(self, row: Tag, css_class: str) -> str:
        """Return the value in the column with the specified CSS class."""
        td = cast("Tag", row.find("td", class_=css_class))
        if span := cast("Tag", td.find("span", class_="ellipsed-name")):
            return span.get_text()
        return td.get_text()
