"""Trello source up-to-dateness collector."""

from datetime import datetime

from dateutil.parser import parse

from base_collectors import SourceUpToDatenessCollector
from collector_utilities.type import Response

from .base import TrelloBase


class TrelloSourceUpToDateness(TrelloBase, SourceUpToDatenessCollector):
    """Collector to measure how up-to-date a Trello board is."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to get the date and time of most recent activity from the cards."""
        json = await response.json()
        cards = json["cards"]
        lists = {lst["id"]: lst["name"] for lst in json["lists"]}
        dates = [json["dateLastActivity"]] + [
            card["dateLastActivity"] for card in cards if not self.__ignore_card(card, lists)
        ]
        return parse(max(dates))

    def __ignore_card(self, card, lists) -> bool:
        """Return whether the card should be ignored."""
        lists_to_ignore = self._parameter("lists_to_ignore")
        return card["idList"] in lists_to_ignore or lists[card["idList"]] in lists_to_ignore
