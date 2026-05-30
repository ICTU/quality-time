"""Base classes for Jira collectors."""

from typing import TYPE_CHECKING

from base_collectors import TokenAuthenticationSourceCollector
from collector_utilities.exceptions import CollectorError
from collector_utilities.type import URL

if TYPE_CHECKING:
    from .json_types import Board


class JiraBase(TokenAuthenticationSourceCollector):
    """Base class for Jira collectors."""

    AUTH_PREFIX = "Bearer "

    def _basic_auth_credentials(self) -> tuple[str, str] | None:
        """Extend to only return the basic auth credentials if no private token is configured.

        This prevents aiohttp from complaining that it "Cannot combine AUTHORIZATION header with AUTH argument or
        credentials encoded in URL".
        """
        return None if self._parameter("private_token") else super()._basic_auth_credentials()

    @property
    def _rest_api_version(self) -> str:
        """Return the Jira REST API version set by the user."""
        return str(self._parameter("api_version"))


class JiraBoardBase(JiraBase):
    """Base class for Jira collectors that use a board."""

    async def _board_id(self, api_url: URL) -> str:
        """Return the board id."""
        last = False
        start_at = 0
        boards: list[Board] = []
        while not last:
            url = URL(f"{api_url}/rest/agile/1.0/board?startAt={start_at}")
            response = (await super()._get_source_responses(url))[0]
            json = await response.json()
            boards.extend(json["values"])
            start_at += json["maxResults"]
            last = json["isLast"]
        board_name_or_id = str(self._parameter("board")).lower()
        matching_boards = [b for b in boards if board_name_or_id in (str(b["id"]), b["name"].lower().strip())]
        if not matching_boards:
            message = f"Could not find a Jira board with id or name '{board_name_or_id}' at {api_url}"
            raise CollectorError(message)
        return str(matching_boards[0]["id"])
