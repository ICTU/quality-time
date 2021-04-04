"""Quality-time specific types."""

from typing import Any, NewType, Optional

import aiohttp


ErrorMessage = Optional[str]
Job = dict[str, Any]
Jobs = list[Job]
JSON = dict[str, Any]
Namespaces = dict[str, str]  # Namespace prefix to Namespace URI mapping
Response = aiohttp.ClientResponse
Responses = list[Response]
URL = NewType("URL", str)
Value = Optional[str]
