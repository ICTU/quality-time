"""Shared test data."""

from typing import cast

from shared.utils.type import MetricId, SourceId, ReportId, SubjectId


METRIC_ID = cast(MetricId, "metric_uuid")
SOURCE_ID = cast(SourceId, "source_uuid")
SUBJECT_ID = cast(SubjectId, "subject_uuid")
REPORT_ID = cast(ReportId, "report_uuid")
REPORT_ID2 = cast(ReportId, "report_uuid2")
