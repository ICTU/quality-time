"""Trello metric collector."""

from datetime import datetime
from typing import cast, Optional

from dateutil.parser import parse
import requests

from ..collector import Collector
from ..type import Unit, Units, URL, Value
from ..util import days_ago


class TrelloIssues(Collector):
    """Collector to get issues (cards) from Trello."""

    def landing_url(self, response: Optional[requests.Response], **parameters) -> URL:
        return f"https://trello.com/b/{response.json()['id']}"

    def get_source_response(self, api_url: URL, **parameters) -> requests.Response:
        """Override because we need to do multiple requests to get all the data we need."""
        api = f"1/boards/{self.board_id(**parameters)}?fields=id,url,dateLastActivity&lists=open&list_fields=name&cards=visible&card_fields=name,closed,dateLastActivity,due,idList,url"
        return requests.get(self.url_with_auth(api, **parameters), timeout=self.TIMEOUT)

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(len(self.parse_source_response_units(response, **parameters)))

    def parse_source_response_units(self, response: requests.Response, **parameters) -> Units:
        json = response.json()
        cards = json["cards"]
        lists = {lst["id"]: lst["name"] for lst in json["lists"]}
        return [self.card_to_unit(card, lists) for card in cards if not self.ignore_card(card, lists, **parameters)]

    def board_id(self, **parameters) -> str:
        """Return the id of the board specified by the user."""
        url = self.url_with_auth("1/members/me/boards?fields=name", **parameters)
        boards = requests.get(url, timeout=self.TIMEOUT).json()
        return [board for board in boards if parameters.get("board") in board.values()][0]["id"]

    @staticmethod
    def ignore_card(card, lists, **parameters) -> bool:
        """Return whether the card should be ignored."""

        def card_is_inactive() -> bool:
            """Return whether the card is inactive."""
            date_last_activity = parse(card["dateLastActivity"])
            return days_ago(date_last_activity) > int(cast(int, parameters.get("inactive_days")))

        def card_is_overdue() -> bool:
            """Return whether the card is overdue."""
            due_date = parse(card["due"]) if card.get("due") else datetime.max
            return due_date < datetime.now(tz=due_date.tzinfo)

        lists_to_ignore = parameters.get("lists_to_ignore") or []
        if card["idList"] in lists_to_ignore or lists[card["idList"]] in lists_to_ignore:
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
    def card_to_unit(card, lists) -> Unit:
        """Convert a card into a unit."""
        return dict(
            key=card["id"], title=card["name"], url=card["url"], list=lists[card["idList"]], due_date=card["due"],
            date_last_activity=card["dateLastActivity"])

    def url_with_auth(self, api_part: str, **parameters) -> str:
        """Return the authentication URL parameters."""
        sep = "&" if "?" in api_part else "?"
        api_key = parameters.get("api_key")
        token = parameters.get("token")
        return f"{self.api_url(**parameters)}/{api_part}{sep}key={api_key}&token={token}"
