"""Quality-time specific types."""

from typing import Literal, NewType, Union

from server_utilities.type import ReportId, SubjectId, MetricId, SourceId

Change = dict[str, Union[str, dict[str, str]]]
EditScope = Literal["source", "metric", "subject", "report", "reports"]
ItemId = Union[ReportId, SubjectId, MetricId, SourceId]
NotificationDestinationId = NewType("NotificationDestinationId", str)
Position = Literal["first", "last", "next", "previous"]
SessionId = NewType("SessionId", str)
URL = NewType("URL", str)
