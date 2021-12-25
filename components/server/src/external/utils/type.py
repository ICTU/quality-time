"""Quality-time specific types."""

from typing import Literal, NewType, Union


EditScope = Literal["source", "metric", "subject", "report", "reports"]
Change = dict[str, Union[str, dict[str, str]]]
SessionId = NewType("SessionId", str)
