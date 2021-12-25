"""Quality-time specific types."""

from typing import Literal, NewType


Color = Literal["green", "grey", "red", "yellow", "white"]
Direction = Literal["<", ">"]
Scale = Literal["count", "percentage", "version_number"]
Status = Literal["target_met", "debt_target_met", "near_target_met", "target_not_met"]
TargetType = Literal["target", "near_target", "debt_target"]

MeasurementId = NewType("MeasurementId", str)
MetricId = NewType("MetricId", str)
ReportId = NewType("ReportId", str)
SourceId = NewType("SourceId", str)
SubjectId = NewType("SubjectId", str)
