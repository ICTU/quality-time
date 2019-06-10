"""Quality-time specific types."""

from typing import Any, Dict, List, NewType, Optional, Sequence, Union


Entity = Dict  # pylint: disable=invalid-name
Entities = List[Entity]
ErrorMessage = Optional[str]
Job = Dict[str, Any]
Jobs = List[Job]
Namespaces = Dict[str, str]  # Namespace prefix to Namespace URI mapping
Response = Dict[str, Any]
URL = NewType("URL", str)
Subject = Dict[str, Union[str, Sequence[URL]]]
Report = Dict[str, Sequence[Subject]]
Value = Optional[str]
Parameter = Union[str, List[str]]
