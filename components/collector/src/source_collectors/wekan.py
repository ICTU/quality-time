"""Wekan metric collector."""

from datetime import datetime
from typing import cast, List

import cachetools.func
from dateutil.parser import parse
import requests

from utilities.type import Entity, Entities, URL, Value
from utilities.functions import days_ago
from .source_collector import SourceCollector


class WekanBase(SourceCollector):
    """Base class for Wekan collectors."""

    def _landing_url(self, responses: List[requests.Response]) -> URL:
        api_url = self._api_url()
        return URL(f"{api_url}/b/{self._board_id(responses[0].json()['token'])}") if responses else api_url

    def _get_source_responses(self, api_url: URL) -> List[requests.Response]:
        """Override because we want to do a post request to login."""
        credentials = dict(username=self._parameter("username"), password=self._parameter("password"))
        return [requests.post(f"{api_url}/users/login", data=credentials, timeout=self.TIMEOUT)]

    def _board_id(self, token) -> str:
        """Return the id of the board specified by the user."""
        api_url = self._api_url()
        user_id = self._get_json(URL(f"{api_url}/api/user"), token)["_id"]
        boards = self._get_json(URL(f"{api_url}/api/users/{user_id}/boards"), token)
        return [board for board in boards if self._parameter("board") in board.values()][0]["_id"]

    def _lists(self, board_url: str, token: str) -> List:
        """Return the lists on the board."""
        return [lst for lst in self._get_json(URL(f"{board_url}/lists"), token) if not self.__ignore_list(lst)]

    def _cards(self, list_url: str, token: str) -> List:
        """Return the cards on the board."""
        cards = self._get_json(URL(f"{list_url}/cards"), token)
        full_cards = [self._get_json(URL(f"{list_url}/cards/{card['_id']}"), token) for card in cards]
        return [card for card in full_cards if not self._ignore_card(card)]

    @cachetools.func.ttl_cache(ttl=60)
    def _get_json(self, api_url: URL, token: str):
        """Get the JSON from the API url."""
        return requests.get(api_url, timeout=self.TIMEOUT, headers=dict(Authorization=f"Bearer {token}")).json()

    def __ignore_list(self, card_list) -> bool:
        """Return whether the list should be ignored."""
        if card_list.get("archived", False):
            return True
        lists_to_ignore = cast(List[str], self._parameter("lists_to_ignore"))
        return card_list["_id"] in lists_to_ignore or card_list["title"] in lists_to_ignore

    def _ignore_card(self, card) -> bool:  # pylint: disable=unused-argument,no-self-use
        """Return whether the card should be ignored."""
        return card.get("archived", False)


class WekanIssues(WekanBase):
    """Collector to get issues (cards) from Wekan."""

    def _parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        return str(len(self._parse_source_responses_entities(responses)))

    def _parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        token = responses[0].json()['token']
        api_url = self._api_url()
        board_url = f"{api_url}/api/boards/{self._board_id(token)}"
        board_slug = self._get_json(URL(board_url), token)["slug"]
        entities: Entities = []
        for lst in self._lists(board_url, token):
            for card in self._cards(f"{board_url}/lists/{lst['_id']}", token):
                entities.append(self.__card_to_entity(card, api_url, board_slug, lst["title"]))
        return entities

    def _ignore_card(self, card) -> bool:

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
        return dict(key=card["_id"], url=f"{api_url}/b/{card['boardId']}/{board_slug}/{card['_id']}",
                    list=list_title, title=card["title"], due_date=card.get("dueAt", ""),
                    date_last_activity=card["dateLastActivity"])


class WekanSourceUpToDateness(WekanBase):
    """Collector to measure how up-to-date a Wekan board is."""

    def _parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        token = responses[0].json()['token']
        board_url = f"{self._api_url()}/api/boards/{self._board_id(token)}"
        board = self._get_json(URL(board_url), token)
        dates = [board.get("createdAt"), board.get("modifiedAt")]
        for lst in self._lists(board_url, token):
            dates.extend([lst.get("createdAt"), lst.get("updatedAt")])
            list_url = f"{board_url}/lists/{lst['_id']}"
            dates.extend([card["dateLastActivity"] for card in self._cards(list_url, token)])
        return str(days_ago(parse(max([date for date in dates if date]))))
