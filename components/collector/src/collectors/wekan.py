"""Wekan metric collector."""

from datetime import datetime
from typing import cast, List

import cachetools.func
from dateutil.parser import parse
import requests

from ..collector import Collector
from ..type import Entity, Entities, URL, Value
from ..util import days_ago


class WekanBase(Collector):
    """Base class for Wekan collectors."""

    def landing_url(self, responses: List[requests.Response], **parameters) -> URL:
        api_url = self.api_url(**parameters)
        return URL(f"{api_url}/b/{self.board_id(responses[0].json()['token'], **parameters)}") if responses else api_url

    def get_source_responses(self, api_url: URL, **parameters) -> List[requests.Response]:
        """Override because we want to do a post request to login."""
        credentials = dict(username=parameters.get("username"), password=parameters.get("password"))
        return [requests.post(f"{api_url}/users/login", data=credentials, timeout=self.TIMEOUT)]

    def board_id(self, token, **parameters) -> str:
        """Return the id of the board specified by the user."""
        api_url = self.api_url(**parameters)
        user_id = self.get_json(f"{api_url}/api/user", token)["_id"]
        boards = self.get_json(f"{api_url}/api/users/{user_id}/boards", token)
        return [board for board in boards if parameters.get("board") in board.values()][0]["_id"]

    def lists(self, board_url: str, token: str, **parameters) -> List:
        """Return the lists on the board."""
        return [lst for lst in self.get_json(f"{board_url}/lists", token)
                if not self.ignore_list(lst, **parameters)]

    def cards(self, list_url: str, token: str, **parameters) -> List:
        """Return the cards on the board."""
        cards = self.get_json(f"{list_url}/cards", token)
        full_cards = [self.get_json(f"{list_url}/cards/{card['_id']}", token) for card in cards]
        return [card for card in full_cards if not self.ignore_card(card, **parameters)]

    @cachetools.func.ttl_cache(ttl=60)
    def get_json(self, api_url: URL, token: str):
        """Get the JSON from the API url."""
        return requests.get(api_url, timeout=self.TIMEOUT, headers=dict(Authorization=f"Bearer {token}")).json()

    def ignore_list(self, card_list, **parmaeters) -> bool:  # pylint: disable=unused-argument,no-self-use
        """Return whether the list should be ignored."""
        return card_list.get("archived", False)

    def ignore_card(self, card, **parameters) -> bool:  # pylint: disable=unused-argument,no-self-use
        """Return whether the card should be ignored."""
        return card.get("archived", False)


class WekanIssues(WekanBase):
    """Collector to get issues (cards) from Wekan."""

    def parse_source_responses_value(self, responses: List[requests.Response], **parameters) -> Value:
        return str(len(self.parse_source_responses_entities(responses, **parameters)))

    def parse_source_responses_entities(self, responses: List[requests.Response], **parameters) -> Entities:
        token = responses[0].json()['token']
        api_url = self.api_url(**parameters)
        board_url = f"{api_url}/api/boards/{self.board_id(token, **parameters)}"
        board_slug = self.get_json(board_url, token)["slug"]
        entities: Entities = []
        for lst in self.lists(board_url, token, **parameters):
            for card in self.cards(f"{board_url}/lists/{lst['_id']}", token, **parameters):
                entities.append(self.card_to_entity(card, api_url, board_slug, lst["title"]))
        return entities

    def ignore_list(self, card_list, **parameters) -> bool:
        if super().ignore_list(card_list, **parameters):
            return True
        lists_to_ignore = parameters.get("lists_to_ignore") or []
        return card_list["_id"] in lists_to_ignore or card_list["title"] in lists_to_ignore

    def ignore_card(self, card, **parameters) -> bool:

        def card_is_inactive() -> bool:
            """Return whether the card is inactive."""
            date_last_activity = parse(card["dateLastActivity"])
            return days_ago(date_last_activity) > int(cast(int, parameters.get("inactive_days")))

        def card_is_overdue() -> bool:
            """Return whether the card is overdue."""
            due_date = parse(card["dueAt"]) if "dueAt" in card else datetime.max
            return due_date < datetime.now(tz=due_date.tzinfo)

        if super().ignore_card(card, **parameters):
            return True
        cards_to_count = parameters.get("cards_to_count") or []
        if "inactive" in cards_to_count and card_is_inactive():
            return False
        if "overdue" in cards_to_count and card_is_overdue():
            return False
        return bool(cards_to_count)

    @staticmethod
    def card_to_entity(card, api_url: URL, board_slug: str, list_title: str) -> Entity:
        """Convert a card into a entity."""
        return dict(key=card["_id"], url=f"{api_url}/b/{card['boardId']}/{board_slug}/{card['_id']}",
                    list=list_title, title=card["title"], due_date=card.get("dueAt", ""),
                    date_last_activity=card["dateLastActivity"])


class WekanSourceUpToDateness(WekanBase):
    """Collector to measure how up-to-date a Wekan board is."""

    def parse_source_responses_value(self, responses: List[requests.Response], **parameters) -> Value:
        token = responses[0].json()['token']
        board_url = f"{self.api_url(**parameters)}/api/boards/{self.board_id(token, **parameters)}"
        board = self.get_json(board_url, token)
        dates = [board.get("createdAt"), board.get("modifiedAt")]
        for lst in self.lists(board_url, token, **parameters):
            dates.extend([lst.get("createdAt"), lst.get("updatedAt")])
            list_url = f"{board_url}/lists/{lst['_id']}"
            dates.extend([card["dateLastActivity"] for card in self.cards(list_url, token, **parameters)])
        return str(days_ago(parse(min([date for date in dates if date]))))
