"""Quality-time specific types."""

from typing import Any, Dict, List, NewType, Optional, Sequence, Union


Job = Dict[str, Any]
Jobs = List[Job]
Namespaces = Dict[str, str]  # Namespace prefix to Namespace URI mapping
URL = NewType("URL", str)
Unit = Dict  # pylint: disable=invalid-name
Units = List[Unit]
Value = Optional[str]
ErrorMessage = Optional[str]
Subject = Dict[str, Union[str, Sequence[URL]]]
Report = Dict[str, Sequence[Subject]]
Response = Dict[str, Any]
