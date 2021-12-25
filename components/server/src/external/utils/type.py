"""Quality-time specific types."""

from typing import Literal, NewType, Union


Change = dict[str, Union[str, dict[str, str]]]
EditScope = Literal["source", "metric", "subject", "report", "reports"]
NotificationDestinationId = NewType("NotificationDestinationId", str)
SessionId = NewType("SessionId", str)
