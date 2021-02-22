"""Quality-time specific types."""

from typing import Literal, NewType, Union

Change = dict[str, Union[str, dict[str, str]]]
Color = Literal["green", "grey", "red", "yellow", "white"]
Direction = Literal["<", ">"]
EditScope = Literal["source", "metric", "subject", "report", "reports"]
Position = Literal["first", "last", "next", "previous"]
Scale = Literal["count", "percentage"]
Status = Literal["target_met", "debt_target_met", "near_target_met", "target_not_met"]
TargetType = Literal["target", "near_target", "debt_target"]

MeasurementId = NewType("MeasurementId", str)
MetricId = NewType("MetricId", str)
NotificationDestinationId = NewType("NotificationDestinationId", str)
ReportId = NewType("ReportId", str)
SessionId = NewType("SessionId", str)
SourceId = NewType("SourceId", str)
SubjectId = NewType("SubjectId", str)
ItemId = Union[ReportId, SubjectId, MetricId, SourceId]
URL = NewType("URL", str)
