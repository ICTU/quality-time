"""Source responses model class."""

from collector_utilities.type import URL, ErrorMessage, Response, Responses


class SourceResponses:
    """Class the hold the source responses, and associated information such as api_url and connection error, if any."""

    def __init__(
        self, *, responses: Responses = None, api_url: URL = None, connection_error: ErrorMessage = None
    ) -> None:
        self.__responses: Responses = responses or []
        self.api_url = api_url
        self.connection_error = connection_error

    def __iter__(self):
        return iter(self.__responses)

    def __len__(self) -> int:
        return len(self.__responses)

    def __getitem__(self, key):
        return self.__responses[key]

    def __setitem__(self, key, value):
        self.__responses[key] = value

    def append(self, response: Response) -> None:
        """Append a response."""
        self.__responses.append(response)

    def insert(self, index, response: Response) -> None:
        """Insert a response."""
        self.__responses.insert(index, response)

    def extend(self, responses: "SourceResponses") -> None:
        """Extend the responses."""
        self.__responses.extend(list(responses))
        if self.__responses is None:
            self.connection_error = responses.connection_error
