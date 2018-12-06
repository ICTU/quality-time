from typing import Any, Dict, NewType, Sequence


URL = NewType("URL", str)
Measurement = str
Measurements = Sequence[Measurement]
ErrorMessage = str
MeasurementResponse = Dict[str, Any]
