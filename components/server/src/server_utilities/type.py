"""Quality-time specific types."""

from typing import Dict, Literal, NewType, Union

Change = Dict[str, Union[str, Dict[str, str]]]
Color = Literal["green", "grey", "red", "yellow", "white"]
Direction = Literal["<", ">"]
EditScope = Literal["source", "metric", "subject", "report", "reports"]
Scale = Literal["count", "percentage"]
Status = Literal["target_met", "debt_target_met", "near_target_met", "target_not_met"]
Position = Literal["first", "last", "next", "previous"]

MeasurementId = NewType("MeasurementId", str)
MetricId = NewType("MetricId", str)
ReportId = NewType("ReportId", str)
SessionId = NewType("SessionId", str)
SourceId = NewType("SourceId", str)
SubjectId = NewType("SubjectId", str)
ItemId = Union[ReportId, SubjectId, MetricId, SourceId]
URL = NewType("URL", str)
