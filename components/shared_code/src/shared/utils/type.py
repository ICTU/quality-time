"""Quality-time specific types."""

from typing import Literal, NewType

Color = Literal["blue", "green", "grey", "red", "yellow", "white"]
Direction = Literal["<", ">"]
Scale = Literal["count", "percentage", "version_number"]
Status = Literal["informative", "target_met", "debt_target_met", "near_target_met", "target_not_met"]
TargetType = Literal["target", "near_target", "debt_target"]
Value = str | None

ItemId = NewType("ItemId", str)
ReportId = NewType("ReportId", ItemId)
SubjectId = NewType("SubjectId", ItemId)
MetricId = NewType("MetricId", ItemId)
SourceId = NewType("SourceId", ItemId)
NotificationDestinationId = NewType("NotificationDestinationId", ItemId)
