"""Quality-time specific types."""

from typing import Literal, NewType, Union

from shared.utils.type import ReportId, SubjectId, MetricId, SourceId

Change = dict[str, Union[str, dict[str, str]]]
EditScope = Literal["source", "metric", "subject", "report", "reports"]
ItemId = Union[ReportId, SubjectId, MetricId, SourceId]
Position = Literal["first", "last", "next", "previous"]
URL = NewType("URL", str)
