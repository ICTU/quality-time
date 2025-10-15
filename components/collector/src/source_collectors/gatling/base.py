"""Base classes for Gatling collectors."""

from abc import ABC
from typing import TYPE_CHECKING, cast

from base_collectors import HTMLFileSourceCollector

if TYPE_CHECKING:
    from bs4 import Tag

    from collector_utilities.type import Response


class GatlingHTMLCollector(HTMLFileSourceCollector, ABC):
    """Base class for Gatling HTML collectors."""

    async def simulation_information(self, response: Response, label: str) -> str:
        """Return the simulation information labeled with the label.

        Gatling simulation meta information is contained in two sibling spans: the first span has the
        "simulation-information-label" CSS class and the label as contents, the second span contains the information.
        """
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
