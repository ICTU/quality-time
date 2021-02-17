"""Wekan issues collector."""

from datetime import datetime
from typing import Dict, cast

from dateutil.parser import parse

from collector_utilities.functions import days_ago
from collector_utilities.type import URL
from source_model import Entity, SourceMeasurement, SourceResponses

from .base import WekanBase


class WekanIssues(WekanBase):
    """Collector to get issues (cards) from Wekan."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the cards."""
        api_url = await self._api_url()
        board_slug = self._board["slug"]
        entities = []
        for lst in self._lists:
            for card in self._cards.get(lst["_id"], []):
                entities.append(self.__card_to_entity(card, api_url, board_slug, lst["title"]))
        return SourceMeasurement(entities=entities)

    def _ignore_card(self, card: Dict) -> bool:
        """Extend to check for card status."""

        def card_is_inactive() -> bool:
            """Return whether the card is inactive."""
            date_last_activity = parse(card["dateLastActivity"])
            return days_ago(date_last_activity) > int(cast(int, self._parameter("inactive_days")))

        def card_is_overdue() -> bool:
            """Return whether the card is overdue."""
            due_date = parse(card["dueAt"]) if "dueAt" in card else datetime.max
            return due_date < datetime.now(tz=due_date.tzinfo)

        if super()._ignore_card(card):
            return True
        cards_to_count = self._parameter("cards_to_count")
        if "inactive" in cards_to_count and card_is_inactive():
            return False
        if "overdue" in cards_to_count and card_is_overdue():
            return False
        return bool(cards_to_count)

    @staticmethod
    def __card_to_entity(card, api_url: URL, board_slug: str, list_title: str) -> Entity:
        """Convert a card into a entity."""
        return Entity(
            key=card["_id"],
            url=f"{api_url}/b/{card['boardId']}/{board_slug}/{card['_id']}",
            list=list_title,
            title=card["title"],
            due_date=card.get("dueAt", ""),
            date_last_activity=card["dateLastActivity"],
        )
