"""Quality-time specific types."""

from dataclasses import dataclass
from typing import Literal, NewType, Union

from shared.utils.type import ReportId, SubjectId, MetricId, SourceId

Change = dict[str, Union[str, dict[str, str]]]
EditScope = Literal["source", "metric", "subject", "report", "reports"]
ItemId = Union[ReportId, SubjectId, MetricId, SourceId]
NotificationDestinationId = NewType("NotificationDestinationId", str)
Position = Literal["first", "last", "next", "previous"]
SessionId = NewType("SessionId", str)
URL = NewType("URL", str)


@dataclass
class User:
    """Class representing a user."""

    username: str
    email: str
