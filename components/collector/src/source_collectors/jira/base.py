"""Base classes for Jira collectors."""

from typing import TYPE_CHECKING

from base_collectors import TokenAuthenticationSourceCollector
from collector_utilities.exceptions import CollectorError

if TYPE_CHECKING:
    from collector_utilities.type import URL, Response

    from .json_types import Board


class JiraError(CollectorError):
    """Jira responded with an error."""

    def __init__(self, status: int, reason: str, error_messages: list[str]) -> None:
        super().__init__(f"Jira responded with HTTP status {status} ({reason}): {' '.join(error_messages)}")


class JiraBase(TokenAuthenticationSourceCollector):
    """Base class for Jira collectors."""

    AUTH_PREFIX = "Bearer "

    @property
    def _rest_api_version(self) -> str:
        """Return the Jira REST API version set by the user."""
        return str(self._parameter("api_version"))

    async def _get_source_response(self, url: URL, headers: dict[str, str]) -> Response:
        """Override to add the error messages that Jira returns to the error, if the request fails.

        The session raises an error without the response body if a request fails, and discards the body. To be able
        to read the error messages from the response body, override the session setting for Jira requests.
        """
        response = await self._session.get(url, allow_redirects=True, headers=headers, raise_for_status=False)
        if not response.ok:
            if error_messages := await self._error_messages(response):
                raise JiraError(response.status, str(response.reason), error_messages)
            response.raise_for_status()
        return response

    @staticmethod
    async def _error_messages(response: Response) -> list[str]:
        """Return the error messages from the Jira response, if any."""
        try:
            json = await response.json(content_type=None)
        except ValueError:  # The response body is not JSON, for example an HTML error page of a proxy
            return []
        if not isinstance(json, dict):
            return []
        return [str(message) for message in json.get("errorMessages") or []] + [
            str(message) for message in (json.get("errors") or {}).values()
        ]


class JiraBoardBase(JiraBase):
    """Base class for Jira collectors that use a board."""

    async def _board_id(self, api_url: URL) -> str:
        """Return the board id."""
        last = False
        start_at = 0
        boards: list[Board] = []
        while not last:
            url = api_url / f"rest/agile/1.0/board?startAt={start_at}"
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
