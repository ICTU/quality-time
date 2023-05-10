"""Source responses model class."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collector_utilities.type import URL, ErrorMessage, Response, Responses


class SourceResponses:
    """Class the hold the source responses, and associated information such as api_url and connection error, if any."""

    def __init__(
        self,
        *,
        responses: Responses | None = None,
        api_url: URL | None = None,
        connection_error: ErrorMessage | None = None,
    ) -> None:
        self.__responses: Responses = responses or []
        self.api_url = api_url
        self.connection_error = connection_error

    def __iter__(self):
        """Return an iterator over the responses."""
        return iter(self.__responses)

    def __len__(self) -> int:
        """Return the number of responses."""
        return len(self.__responses)

    def __getitem__(self, index):
        """Return a response by index."""
        return self.__responses[index]

    def __setitem__(self, index, response) -> None:
        """Set a response by index."""
        self.__responses[index] = response

    def append(self, response: Response) -> None:
        """Append a response."""
        self.__responses.append(response)

    def insert(self, index: int, response: Response) -> None:
        """Insert a response."""
        self.__responses.insert(index, response)

    def extend(self, responses: SourceResponses) -> None:
        """Extend the responses."""
        self.__responses.extend(list(responses))
