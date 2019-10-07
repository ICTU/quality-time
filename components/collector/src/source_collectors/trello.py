"""Trello metric collector."""

from abc import ABC
from datetime import datetime
from typing import cast

from dateutil.parser import parse
import requests

from utilities.type import Entity, Entities, Responses, URL, Value
from utilities.functions import days_ago
from .source_collector import SourceCollector


class TrelloBase(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for Trello collectors."""

    def _landing_url(self, responses: Responses) -> URL:
        return URL(responses[0].json()["url"] if responses else "https://trello.com")

    def _get_source_responses(self, api_url: URL) -> Responses:
        """Override because we need to do multiple requests to get all the data we need."""
        api = f"1/boards/{self.__board_id()}?fields=id,url,dateLastActivity&lists=open&" \
            "list_fields=name&cards=visible&card_fields=name,dateLastActivity,due,idList,url"
        return [requests.get(self.__url_with_auth(api), timeout=self.TIMEOUT)]

    def __board_id(self) -> str:
        """Return the id of the board specified by the user."""
        url = self.__url_with_auth("1/members/me/boards?fields=name")
        boards = requests.get(url, timeout=self.TIMEOUT).json()
        return str([board for board in boards if self._parameter("board") in board.values()][0]["id"])

    def __url_with_auth(self, api_part: str) -> str:
        """Return the authentication URL parameters."""
        sep = "&" if "?" in api_part else "?"
        api_key = self._parameter("api_key")
        token = self._parameter("token")
        return f"{self._api_url()}/{api_part}{sep}key={api_key}&token={token}"


class TrelloIssues(TrelloBase):
    """Collector to get issues (cards) from Trello."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(len(self._parse_source_responses_entities(responses)))

    def _parse_source_responses_entities(self, responses: Responses) -> Entities:
        json = responses[0].json()
        cards = json["cards"]
        lists = {lst["id"]: lst["name"] for lst in json["lists"]}
        return [self.__card_to_entity(card, lists) for card in cards if not self._ignore_card(card, lists)]

    def _ignore_card(self, card, lists) -> bool:
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
        return dict(
            key=card["id"], title=card["name"], url=card["url"], list=lists[card["idList"]], due_date=card["due"],
            date_last_activity=card["dateLastActivity"])


class TrelloSourceUpToDateness(TrelloBase):
    """Collector to measure how up-to-date a Trello board is."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        json = responses[0].json()
        cards = json["cards"]
        lists = {lst["id"]: lst["name"] for lst in json["lists"]}
        dates = [json["dateLastActivity"]] + \
                [card["dateLastActivity"] for card in cards if not self._ignore_card(card, lists)]
        return str(days_ago(parse(max(dates))))

    def _ignore_card(self, card, lists) -> bool:
        """Return whether the card should be ignored."""
        lists_to_ignore = self._parameter("lists_to_ignore")
        return card["idList"] in lists_to_ignore or lists[card["idList"]] in lists_to_ignore
