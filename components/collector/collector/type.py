"""Quality-time specific types."""

from typing import Any, Dict, List, NewType, Sequence, Union


URL = NewType("URL", str)
Measurement = Union[str, List[Dict]]
ErrorMessage = str
Subject = Dict[str, Union[str, Sequence[URL]]]
Report = Dict[str, Sequence[Subject]]
Response = Dict[str, Any]
