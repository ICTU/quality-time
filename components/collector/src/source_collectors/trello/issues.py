"""Trello issues collector."""

from datetime import datetime
from typing import cast

from dateutil.parser import parse

from collector_utilities.functions import days_ago
from model import Entities, Entity, SourceResponses

from .base import TrelloBase


class TrelloIssues(TrelloBase):
    """Collector to get issues (cards) from Trello."""

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the issues from the JSON."""
        json = await responses[0].json()
        cards = json["cards"]
        lists = {lst["id"]: lst["name"] for lst in json["lists"]}
        return Entities(self.__card_to_entity(card, lists) for card in cards)

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether the card should be included."""

        def card_is_inactive() -> bool:
            """Return whether the card is inactive."""
            date_last_activity = parse(entity["date_last_activity"])
            return days_ago(date_last_activity) > int(cast(int, self._parameter("inactive_days")))

        def card_is_overdue() -> bool:
            """Return whether the card is overdue."""
            due_date = parse(entity["due_date"]) if entity["due_date"] else datetime.max
            return due_date < datetime.now(tz=due_date.tzinfo)

        lists_to_ignore = self._parameter("lists_to_ignore")
        if entity["id_list"] in lists_to_ignore or entity["list"] in lists_to_ignore:
            return False

        cards_to_count = self._parameter("cards_to_count")  # this parameter is not inclusive; it is "if and only if"
        if "overdue" in cards_to_count and card_is_overdue():
            return True
        if "inactive" in cards_to_count and card_is_inactive():
            return True
        return not bool(cards_to_count)  # only include if the parameter is empty, i.e. when selecting "all cards"

    @staticmethod
    def __card_to_entity(card, lists) -> Entity:
        """Convert a card into a entity."""
        return Entity(
            key=card["id"],
            title=card["name"],
            url=card["url"],
            id_list=card["idList"],
            list=lists[card["idList"]],
            due_date=card.get("due", ""),
            date_last_activity=card["dateLastActivity"],
        )
