"""Quality-time specific types."""

from typing import Any, Dict, NewType, Optional, Sequence, Tuple, Union


URL = NewType("URL", str)
Unit = Dict  # pylint: disable=invalid-name
Units = Sequence[Unit]
Value = Optional[str]
Measurement = Union[Value, Tuple[Value, Units]]
ErrorMessage = Optional[str]
Subject = Dict[str, Union[str, Sequence[URL]]]
Report = Dict[str, Sequence[Subject]]
Response = Dict[str, Any]
