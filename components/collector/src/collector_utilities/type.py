"""Quality-time specific types."""

from typing import Any, NewType
from xml.etree.ElementTree import Element  # nosec # Element is not available from defusedxml, but only used as type

import aiohttp

type ElementMap = dict[Element, Element]

type ErrorMessage = None | str
type JSONList = list[dict[str, Any]]
type JSONDict = dict[str, Any]
type JSON = JSONDict | JSONList
type Namespaces = dict[str, str]  # Namespace prefix to Namespace URI mapping
type Response = aiohttp.ClientResponse
type Responses = list[Response]
URL = NewType("URL", str)
Value = None | str
