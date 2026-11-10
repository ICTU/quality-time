"""Quality-time specific types."""

from typing import Any
from xml.etree.ElementTree import Element  # nosec # Element is not available from defusedxml, but only used as type

import aiohttp

type ElementMap = dict[Element, Element]

type ErrorMessage = str | None
type InfoMessage = str | None
type JSONList = list[dict[str, Any]]
type JSONDict = dict[str, Any]
type JSON = JSONDict | JSONList
type Namespaces = dict[str, str]  # Namespace prefix to Namespace URI mapping
type Response = aiohttp.ClientResponse
type Responses = list[Response]


class URL(str):
    """URL that can join path segments without duplicate or missing slashes, like pathlib.Path joins paths.

    For example, URL("https://example.org/") / "/api" / "v4" returns URL("https://example.org/api/v4").

    Joining inserts the path before the query string and fragment, if any. Other than the slashes where the path
    is joined, the URL and the path are not changed: they are not normalized or quoted.
    """

    __slots__ = ()

    def __truediv__(self, path: str) -> URL:
        """Return a new URL with the path appended."""
        if not path:
            return self
        end_of_path = len(self.partition("?")[0].partition("#")[0])  # The path ends at the first "?" or "#", if any
        base, query_and_fragment = self[:end_of_path], self[end_of_path:]
        return URL(f"{base.rstrip('/')}/{path.lstrip('/')}{query_and_fragment}")


Value = None | str
