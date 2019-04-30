"""Trello metric collector."""

from datetime import datetime
from typing import cast, List, Optional

import cachetools.func
from dateutil.parser import parse
import requests

from ..collector import Collector
from ..type import Unit, Units, URL, Value
from ..util import days_ago


class TrelloIssues(Collector):
    """Collector to get issues (cards) from Trello."""

    def landing_url(self, response: Optional[requests.Response], **parameters) -> URL:
        return "https://trello.com"
        #return URL(f"{self.api_url(**parameters)}/b/{self.board_id(**parameters)}")

    def get_source_response(self, api_url: URL, **parameters) -> requests.Response:
        """Override because we want to do a post request to login."""
        board_id = parameters.get("board")
        url = f"{api_url}/1/boards/{board_id}/?fields=id,url,dateLastActivity&lists=open&list_fields=name&cards=visible&card_fields=name,closed,dateLastActivity,due,idList,url"
        return requests.get(
            f"{url}&key={parameters.get('api_key')}&token={parameters.get('token')}",
            timeout=self.TIMEOUT)

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(len(self.parse_source_response_units(response, **parameters)))

    def parse_source_response_units(self, response: requests.Response, **parameters) -> Units:
        json = response.json()
        lists = json["lists"]
        cards = json["cards"]
        import logging
        logging.info(lists, cards)
        return []
        units: Units = []
        for lst in self.lists(board_url, **parameters):
            for card in self.cards(f"{board_url}/lists/{lst['_id']}", **parameters):
                units.append(self.card_to_unit(card, api_url, board_slug, lst["title"]))
        return units

    def board_id(self, **parameters) -> str:
        """Return the id of the board specified by the user."""
        boards = self.get_json(f"{self.api_url(**parameters)}/1/members/me/boards?fields=name", **parameters)
        return [board for board in boards if parameters.get("board") in board.values()][0]["id"]

    def lists(self, board_url: str, **parameters) -> List:
        """Return the lists on the board."""
        return [lst for lst in self.get_json(f"{board_url}/lists", **parameters)
                if not self.ignore_list(lst, **parameters)]

    def cards(self, list_url: str, **parameters) -> List:
        """Return the cards on the board."""
        cards = self.get_json(f"{list_url}/cards", **parameters)
        full_cards = [self.get_json(f"{list_url}/cards/{card['_id']}", **parameters) for card in cards]
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
                    list=list_title, title=card["title"], due_date=card.get("dueAt", ""),
                    date_last_activity=card["dateLastActivity"])

    #@cachetools.func.ttl_cache(ttl=60)
    def get_json(self, api_url: URL, **parameters):
        """Get the JSON from the API url."""
        sep = "&" if "?" in api_url else "?"
        return requests.get(
            f"{api_url}{sep}key={parameters.get('api_key')}&token={parameters.get('token')}",
            timeout=self.TIMEOUT).json()
