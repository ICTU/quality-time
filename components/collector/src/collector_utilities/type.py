"""Quality-time specific types."""

from typing import Any, Dict, List, NewType, Optional

import aiohttp


Entity = Dict[str, str]  # pylint: disable=invalid-name
Entities = List[Entity]
ErrorMessage = Optional[str]
Job = Dict[str, Any]
Jobs = List[Job]
JSON = Dict[str, Any]
Namespaces = Dict[str, str]  # Namespace prefix to Namespace URI mapping
Response = aiohttp.ClientResponse
Responses = List[Response]
URL = NewType("URL", str)
Value = Optional[str]
