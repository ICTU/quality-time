"""Quality-time specific types."""

from typing import Any, NewType, Optional, Union

import aiohttp


ErrorMessage = Optional[str]
Job = dict[str, Any]
Jobs = list[Job]
JSONList = list[dict[str, Any]]
JSONDict = dict[str, Any]
JSON = Union[JSONDict, JSONList]
Namespaces = dict[str, str]  # Namespace prefix to Namespace URI mapping
Response = aiohttp.ClientResponse
Responses = list[Response]
URL = NewType("URL", str)
Value = Optional[str]
