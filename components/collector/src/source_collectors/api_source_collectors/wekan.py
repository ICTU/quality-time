"""Wekan metric collector."""

from abc import ABC
from datetime import datetime
from typing import cast, Dict, List, Tuple

from dateutil.parser import parse

from collector_utilities.type import Entity, Entities, Responses, URL, Value
from collector_utilities.functions import days_ago
from base_collectors import SourceCollector


WekanCard = Dict[str, str]
WekanBoard = Dict[str, str]
WekanList = Dict[str, str]


class WekanBase(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for Wekan collectors."""

    def __init__(self, *args, **kwargs) -> None:
        self.__token = ""
        self._board: WekanBoard = {}
        self._board_url = ""
        self._lists: List[WekanList] = []
        self._cards: Dict[str, List[WekanCard]] = {}
        super().__init__(*args, **kwargs)

    async def _landing_url(self, responses: Responses) -> URL:
        api_url = await self._api_url()
        return URL(f"{api_url}/b/{self._board['_id']}") if responses else api_url

    def _headers(self) -> Dict[str, str]:
        return dict(Authorization=f"Bearer {self.__token}")

    async def _get_source_responses(self, *urls: URL) -> Responses:
        """Override because we want to do a post request to login."""
        credentials = dict(username=self._parameter("username"), password=self._parameter("password"))
        response = await self._session.post(f"{urls[0]}/users/login", data=credentials)
        self.__token = (await response.json())["token"]
        await self.__get_board()
        await self.__get_lists()
        await self.__get_cards()
        return [response]

    async def __get_board(self) -> None:
        """Return the board specified by the user."""
        api_url = await self._api_url()
        user_id = (await self._get_json(URL(f"{api_url}/api/user")))["_id"]
        boards = await self._get_json(URL(f"{api_url}/api/users/{user_id}/boards"))
        self._board = [board for board in boards if self._parameter("board") in board.values()][0]
        self._board_url = f"{api_url}/api/boards/{self._board['_id']}"

    async def __get_lists(self) -> None:
        """Return the lists on the board."""
        self._lists = [
            lst for lst in await self._get_json(URL(f"{self._board_url}/lists"))
            if not self.__ignore_list(lst)]

    async def __get_cards(self) -> None:
        """Get the cards for the list."""
        for lst in self._lists:
            list_url = f"{self._board_url}/lists/{lst['_id']}"
            cards = await self._get_json(URL(f"{list_url}/cards"))
            full_cards = [await self._get_json(URL(f"{list_url}/cards/{card['_id']}")) for card in cards]
            self._cards[lst["_id"]] = [card for card in full_cards if not self._ignore_card(card)]

    async def _get_json(self, api_url: URL):
        """Get the JSON from the API url."""
        return await (await super()._get_source_responses(api_url))[0].json()

    def __ignore_list(self, card_list) -> bool:
        """Return whether the list should be ignored."""
        if card_list.get("archived", False):
            return True
        lists_to_ignore = cast(List[str], self._parameter("lists_to_ignore"))
        return card_list["_id"] in lists_to_ignore or card_list["title"] in lists_to_ignore

    def _ignore_card(self, card: Dict) -> bool:  # pylint: disable=unused-argument,no-self-use
        """Return whether the card should be ignored."""
        return card.get("archived", False)


class WekanIssues(WekanBase):
    """Collector to get issues (cards) from Wekan."""

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        api_url = await self._api_url()
        board_slug = self._board["slug"]
        entities: Entities = []
        for lst in self._lists:
            for card in self._cards.get(lst["_id"], []):
                entities.append(self.__card_to_entity(card, api_url, board_slug, lst["title"]))
        return str(len(entities)), "100", entities

    def _ignore_card(self, card: Dict) -> bool:

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

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        dates = [self._board.get("createdAt"), self._board.get("modifiedAt")]
        for lst in self._lists:
            dates.extend([lst.get("createdAt"), lst.get("updatedAt")])
            dates.extend([card["dateLastActivity"] for card in self._cards.get(lst["_id"], [])])
        return str(days_ago(parse(max([date for date in dates if date])))), "100", []
