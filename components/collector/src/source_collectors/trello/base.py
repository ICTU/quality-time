"""Trello metric collector base classes."""

from abc import ABC

from base_collectors import SourceCollector
from collector_utilities.type import URL
from model import SourceResponses


class TrelloBase(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for Trello collectors."""

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Override to get the landing URL from the response."""
        return URL((await responses[0].json())["url"] if responses else "https://trello.com")

    async def _get_source_responses(self, *urls: URL, **kwargs) -> SourceResponses:
        """Extend to add authentication and field parameters to the URL."""
        api = (
            f"1/boards/{await self.__board_id()}?fields=id,url,dateLastActivity&lists=open&"
            "list_fields=name&cards=visible&card_fields=name,dateLastActivity,due,idList,url"
        )
        return await super()._get_source_responses(await self.__url_with_auth(api), **kwargs)

    async def __board_id(self) -> str:
        """Return the id of the board specified by the user."""
        url = await self.__url_with_auth("1/members/me/boards?fields=name")
        boards = await (await super()._get_source_responses(url))[0].json()
        return str([board for board in boards if self._parameter("board") in board.values()][0]["id"])

    async def __url_with_auth(self, api_part: str) -> URL:
        """Return the authentication URL parameters."""
        sep = "&" if "?" in api_part else "?"
        api_key = self._parameter("api_key")
        token = self._parameter("token")
        return URL(f"{await self._api_url()}/{api_part}{sep}key={api_key}&token={token}")
