"""Shared test data."""

from typing import cast

from utilities.type import MetricId, ReportId, SourceId, SubjectId


METRIC_ID = cast(MetricId, "metric_uuid")
REPORT_ID = cast(ReportId, "report_uuid")
SOURCE_ID = cast(SourceId, "source_uuid")
SOURCE_ID2 = cast(SourceId, "source_uuid2")
SUBJECT_ID = cast(SubjectId, "subject_uuid")
SUBJECT_ID2 = cast(SubjectId, "subject_uuid2")
