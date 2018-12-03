from typing import Dict, NewType, Optional, Union


URL = NewType("URL", str)
Measurement = str
ErrorMessage = str
MeasurementResponse = Dict[str, Union[Optional[str], Optional[URL], Optional[Measurement], Optional[ErrorMessage]]]
