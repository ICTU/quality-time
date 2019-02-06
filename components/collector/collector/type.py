"""Quality-time specific types."""

from typing import Any, Dict, NewType, Sequence, Union


URL = NewType("URL", str)
Measurement = str
Measurements = Sequence[Measurement]
ErrorMessage = str
Subject = Dict[str, Union[str, Sequence[URL]]]
Report = Dict[str, Sequence[Subject]]
Response = Dict[str, Any]
Metric = Dict[str, Any]
