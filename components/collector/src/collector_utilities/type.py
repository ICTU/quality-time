"""Quality-time specific types."""

from typing import Any, NewType
from xml.etree.ElementTree import Element  # nosec # Element is not available from defusedxml, but only used as type

import aiohttp

ElementMap = dict[Element, Element]

ErrorMessage = None | str
Job = dict[str, Any]
JSONList = list[dict[str, Any]]
JSONDict = dict[str, Any]
JSON = JSONDict | JSONList
Namespaces = dict[str, str]  # Namespace prefix to Namespace URI mapping
Response = aiohttp.ClientResponse
Responses = list[Response]
URL = NewType("URL", str)
Value = None | str
