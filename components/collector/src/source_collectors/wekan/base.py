"""Wekan collector base classes."""

from abc import ABC
from typing import Dict, List, cast

from base_collectors import SourceCollector
from collector_utilities.type import URL
from source_model import SourceResponses


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

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Override to create the landing URL."""
        api_url = await self._api_url()
        return URL(f"{api_url}/b/{self._board['_id']}") if responses else api_url

    def _headers(self) -> Dict[str, str]:
        """Override to add the token to the headers."""
        return dict(Authorization=f"Bearer {self.__token}")

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Override because we want to do a post request to login."""
        api_url = urls[0]
        credentials = dict(username=self._parameter("username"), password=self._parameter("password"))
        response = await self._session.post(f"{api_url}/users/login", data=credentials)
        self.__token = (await response.json())["token"]
        await self.__get_board()
        await self.__get_lists()
        await self.__get_cards()
        return SourceResponses(responses=[response], api_url=api_url)

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
            lst for lst in await self._get_json(URL(f"{self._board_url}/lists")) if not self.__ignore_list(lst)
        ]

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
