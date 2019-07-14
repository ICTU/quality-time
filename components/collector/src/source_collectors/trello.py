"""Trello metric collector."""

from datetime import datetime
from typing import cast, List

from dateutil.parser import parse
import requests

from ..source_collector import SourceCollector
from ..type import Entity, Entities, URL, Value
from ..util import days_ago


class TrelloBase(SourceCollector):
    """Base class for Trello collectors."""

    def landing_url(self, responses: List[requests.Response]) -> URL:
        return URL(responses[0].json()["url"] if responses else "https://trello.com")

    def get_source_responses(self, api_url: URL) -> List[requests.Response]:
        """Override because we need to do multiple requests to get all the data we need."""
        api = f"1/boards/{self.board_id()}?fields=id,url,dateLastActivity&lists=open&" \
            "list_fields=name&cards=visible&card_fields=name,dateLastActivity,due,idList,url"
        return [requests.get(self.url_with_auth(api), timeout=self.TIMEOUT)]

    def board_id(self) -> str:
        """Return the id of the board specified by the user."""
        url = self.url_with_auth("1/members/me/boards?fields=name")
        boards = requests.get(url, timeout=self.TIMEOUT).json()
        return [board for board in boards if self.parameters.get("board") in board.values()][0]["id"]

    def url_with_auth(self, api_part: str) -> str:
        """Return the authentication URL parameters."""
        sep = "&" if "?" in api_part else "?"
        api_key = self.parameters.get("api_key")
        token = self.parameters.get("token")
        return f"{self.api_url()}/{api_part}{sep}key={api_key}&token={token}"


class TrelloIssues(TrelloBase):
    """Collector to get issues (cards) from Trello."""

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        return str(len(self.parse_source_responses_entities(responses)))

    def parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        json = responses[0].json()
        cards = json["cards"]
        lists = {lst["id"]: lst["name"] for lst in json["lists"]}
        return [self.card_to_entity(card, lists) for card in cards if not self.ignore_card(card, lists)]

    def ignore_card(self, card, lists) -> bool:
        """Return whether the card should be ignored."""

        def card_is_inactive() -> bool:
            """Return whether the card is inactive."""
            date_last_activity = parse(card["dateLastActivity"])
            return days_ago(date_last_activity) > int(cast(int, self.parameters.get("inactive_days")))

        def card_is_overdue() -> bool:
            """Return whether the card is overdue."""
            due_date = parse(card["due"]) if card.get("due") else datetime.max
            return due_date < datetime.now(tz=due_date.tzinfo)

        lists_to_ignore = self.parameters.get("lists_to_ignore") or []
        if card["idList"] in lists_to_ignore or lists[card["idList"]] in lists_to_ignore:
            return True
        cards_to_count = self.parameters.get("cards_to_count") or []
        if "overdue" in cards_to_count and card_is_overdue():
            return False
        if "inactive" in cards_to_count and card_is_inactive():
            return False
        return bool(cards_to_count)

    @staticmethod
    def card_to_entity(card, lists) -> Entity:
        """Convert a card into a entity."""
        return dict(
            key=card["id"], title=card["name"], url=card["url"], list=lists[card["idList"]], due_date=card["due"],
            date_last_activity=card["dateLastActivity"])


class TrelloSourceUpToDateness(TrelloBase):
    """Collector to measure how up-to-date a Trello board is."""

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        json = responses[0].json()
        dates = [json["dateLastActivity"]] + [card["dateLastActivity"] for card in json["cards"]]
        return str(days_ago(parse(min(dates))))
