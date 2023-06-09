"""Quality-time specific types."""

from typing import Literal, NewType


Change = dict[str, str | dict[str, str]]
EditScope = Literal["source", "metric", "subject", "report", "reports"]
Position = Literal["first", "last", "next", "previous"]
URL = NewType("URL", str)
