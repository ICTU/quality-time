"""Wekan metric collector."""

from datetime import datetime
from typing import cast, List, Optional

import cachetools.func
from dateutil.parser import parse
import requests

from ..collector import Collector
from ..type import Unit, Units, URL, Value
from ..util import days_ago


class WekanIssues(Collector):
    """Collector to get issues (cards) from Wekan."""

    def landing_url(self, response: Optional[requests.Response], **parameters) -> URL:
        api_url = self.api_url(**parameters)
        return URL(f"{api_url}/b/{self.board_id(response.json()['token'], **parameters)}") if response else api_url

    def get_source_response(self, api_url: URL, **parameters) -> requests.Response:
        """Override because we want to do a post request to login."""
        credentials = dict(username=parameters.get("username"), password=parameters.get("password"))
        return requests.post(f"{api_url}/users/login", data=credentials, timeout=self.TIMEOUT)

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(len(self.parse_source_response_units(response, **parameters)))

    def parse_source_response_units(self, response: requests.Response, **parameters) -> Units:
        token = response.json()['token']
        api_url = self.api_url(**parameters)
        board_url = f"{api_url}/api/boards/{self.board_id(token, **parameters)}"
        board_slug = self.get_json(board_url, token)["slug"]
        units: Units = []
        for lst in self.lists(board_url, token, **parameters):
            for card in self.cards(f"{board_url}/lists/{lst['_id']}", token, **parameters):
                units.append(self.card_to_unit(card, api_url, board_slug, lst["title"]))
        return units

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

    @staticmethod
    def ignore_list(card_list, **parameters) -> bool:
        """Return whether the list should be ignored."""
        lists_to_ignore = parameters.get("lists_to_ignore") or []
        return card_list["_id"] in lists_to_ignore or card_list["title"] in lists_to_ignore

    @staticmethod
    def ignore_card(card, **parameters) -> bool:
        """Return whether the card should be ignored."""

        def card_is_inactive() -> bool:
            """Return whether the card is inactive."""
            date_last_activity = parse(card["dateLastActivity"])
            return days_ago(date_last_activity) > int(cast(int, parameters.get("inactive_days")))

        def card_is_overdue() -> bool:
            """Return whether the card is overdue."""
            due_date = parse(card["dueAt"]) if "dueAt" in card else datetime.max
            return due_date < datetime.now(tz=due_date.tzinfo)

        if card["archived"]:
            return True
        cards_to_count = parameters.get("cards_to_count")
        if not cards_to_count:
            return False
        if "overdue" in cards_to_count and card_is_overdue():
            return False
        if "inactive" in cards_to_count and card_is_inactive():
            return False
        return True

    @staticmethod
    def card_to_unit(card, api_url: URL, board_slug: str, list_title: str) -> Unit:
        """Convert a card into a unit."""
        return dict(key=card["_id"], url=f"{api_url}/b/{card['boardId']}/{board_slug}/{card['_id']}",
                    list=list_title, title=card["title"])

    @cachetools.func.ttl_cache(ttl=60)
    def get_json(self, api_url: URL, token: str):
        """Get the JSON from the API url."""
        return requests.get(api_url, timeout=self.TIMEOUT, headers=dict(Authorization=f"Bearer {token}")).json()
