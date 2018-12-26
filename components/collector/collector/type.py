"""Quality-time specific types."""

from typing import Any, Dict, NewType, Sequence


URL = NewType("URL", str)
Measurement = str
Measurements = Sequence[Measurement]
ErrorMessage = str
Response = Dict[str, Any]
