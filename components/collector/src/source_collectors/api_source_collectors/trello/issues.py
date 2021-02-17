"""Trello issues collector."""

from datetime import datetime
from typing import cast

from dateutil.parser import parse

from collector_utilities.functions import days_ago
from source_model import Entity, SourceMeasurement, SourceResponses

from .base import TrelloBase


class TrelloIssues(TrelloBase):
    """Collector to get issues (cards) from Trello."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        json = await responses[0].json()
        cards = json["cards"]
        lists = {lst["id"]: lst["name"] for lst in json["lists"]}
        entities = [self.__card_to_entity(card, lists) for card in cards if not self.__ignore_card(card, lists)]
        return SourceMeasurement(entities=entities)

    def __ignore_card(self, card, lists) -> bool:
        """Return whether the card should be ignored."""

        def card_is_inactive() -> bool:
            """Return whether the card is inactive."""
            date_last_activity = parse(card["dateLastActivity"])
            return days_ago(date_last_activity) > int(cast(int, self._parameter("inactive_days")))

        def card_is_overdue() -> bool:
            """Return whether the card is overdue."""
            due_date = parse(card["due"]) if card.get("due") else datetime.max
            return due_date < datetime.now(tz=due_date.tzinfo)

        lists_to_ignore = self._parameter("lists_to_ignore")
        if card["idList"] in lists_to_ignore or lists[card["idList"]] in lists_to_ignore:
            return True
        cards_to_count = self._parameter("cards_to_count")
        if "overdue" in cards_to_count and card_is_overdue():
            return False
        if "inactive" in cards_to_count and card_is_inactive():
            return False
        return bool(cards_to_count)

    @staticmethod
    def __card_to_entity(card, lists) -> Entity:
        """Convert a card into a entity."""
        return Entity(
            key=card["id"],
            title=card["name"],
            url=card["url"],
            list=lists[card["idList"]],
            due_date=card["due"],
            date_last_activity=card["dateLastActivity"],
        )
