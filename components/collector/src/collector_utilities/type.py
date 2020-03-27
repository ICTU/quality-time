"""Quality-time specific types."""

from typing import Any, Dict, List, NewType, Optional, Union

import aiohttp


Entity = Dict[str, Union[int, float, str]]  # pylint: disable=invalid-name
Entities = List[Entity]
ErrorMessage = Optional[str]
Job = Dict[str, Any]
Jobs = List[Job]
JSON = Dict[str, Any]
Namespaces = Dict[str, str]  # Namespace prefix to Namespace URI mapping
Measurement = Dict[str, Any]
Response = aiohttp.ClientResponse
Responses = List[Response]
URL = NewType("URL", str)
Value = Optional[str]
