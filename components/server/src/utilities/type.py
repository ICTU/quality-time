"""Quality-time specific types."""

from typing import Literal, NewType

Addition = Literal["max", "min", "sum"]
Color = Literal["green", "grey", "red", "yellow", "white"]
Direction = Literal["<", ">"]
Scale = Literal["count", "percentage"]
Status = Literal["target_met", "debt_target_met", "near_target_met", "target_not_met"]
Position = Literal["first", "last", "next", "previous"]

MeasurementId = NewType("MeasurementId", str)
MetricId = NewType("MetricId", str)
ReportId = NewType("ReportId", str)
SessionId = NewType("SessionId", str)
SourceId = NewType("SourceId", str)
SubjectId = NewType("SubjectId", str)
