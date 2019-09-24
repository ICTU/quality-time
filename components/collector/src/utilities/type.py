"""Quality-time specific types."""

from typing import Any, Dict, List, NewType, Optional, Union


Entity = Dict[str, Union[int, str]]  # pylint: disable=invalid-name
Entities = List[Entity]
ErrorMessage = Optional[str]
Job = Dict[str, Any]
Jobs = List[Job]
Namespaces = Dict[str, str]  # Namespace prefix to Namespace URI mapping
Response = Dict[str, Any]
URL = NewType("URL", str)
Value = Optional[str]
