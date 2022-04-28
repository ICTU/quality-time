"""Shared test data."""

from typing import cast

from shared.utils.type import MetricId, SourceId, ReportId, SubjectId, NotificationDestinationId


METRIC_ID = cast(MetricId, "metric_uuid")
METRIC_ID2 = cast(MetricId, "metric_uuid2")
METRIC_ID3 = cast(MetricId, "metric_uuid3")
METRIC_ID4 = cast(MetricId, "metric_uuid4")
NOTIFICATION_DESTINATION_ID = cast(NotificationDestinationId, "destination_uuid")
SOURCE_ID = cast(SourceId, "source_uuid")
SOURCE_ID2 = cast(SourceId, "source_uuid2")
SOURCE_ID3 = cast(SourceId, "source_uuid3")
SOURCE_ID4 = cast(SourceId, "source_uuid4")
SOURCE_ID5 = cast(SourceId, "source_uuid5")
SOURCE_ID6 = cast(SourceId, "source_uuid6")
SOURCE_ID7 = cast(SourceId, "source_uuid7")
SUBJECT_ID = cast(SubjectId, "subject_uuid")
SUBJECT_ID2 = cast(SubjectId, "subject_uuid2")
SUBJECT_ID3 = cast(SubjectId, "subject_uuid3")
REPORT_ID = cast(ReportId, "report_uuid")
REPORT_ID2 = cast(ReportId, "report_uuid2")
