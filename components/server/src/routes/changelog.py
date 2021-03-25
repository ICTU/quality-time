"""Changelog routes."""

from typing import cast

import bottle
from pymongo.database import Database

from database import measurements, reports
from server_utilities.type import MetricId, ReportId, SourceId, SubjectId


def _get_changelog(database: Database, nr_changes: str, **uuids: str):
    """Return the recent most nr_changes changes from the changelog."""
    limit = int(nr_changes)
    changes = [
        dict(
            delta=item["delta"]["description"],
            email=item["delta"].get("email", ""),
            timestamp=item.get("timestamp") or item["start"],
        )
        for item in list(measurements.changelog(database, limit, **uuids))
        + list(reports.changelog(database, limit, **uuids))
    ]
    return dict(changelog=sorted(changes, reverse=True, key=lambda change: cast(str, change["timestamp"]))[:limit])


@bottle.get("/api/v3/changelog/source/<source_uuid>/<nr_changes>", authentication_required=False)
def get_source_changelog(source_uuid: SourceId, nr_changes: str, database: Database):
    """Return the recent most nr_changes changes from the source changelog."""
    return _get_changelog(database, nr_changes, source_uuid=source_uuid)


@bottle.get("/api/v3/changelog/metric/<metric_uuid>/<nr_changes>", authentication_required=False)
def get_metric_changelog(metric_uuid: MetricId, nr_changes: str, database: Database):
    """Return the recent most nr_changes changes from the metric changelog."""
    return _get_changelog(database, nr_changes, metric_uuid=metric_uuid)


@bottle.get("/api/v3/changelog/subject/<subject_uuid>/<nr_changes>", authentication_required=False)
def get_subject_changelog(subject_uuid: SubjectId, nr_changes: str, database: Database):
    """Return the recent most nr_changes changes from the subject changelog."""
    return _get_changelog(database, nr_changes, subject_uuid=subject_uuid)


@bottle.get("/api/v3/changelog/report/<report_uuid>/<nr_changes>", authentication_required=False)
def get_report_changelog(report_uuid: ReportId, nr_changes: str, database: Database):
    """Return the recent most nr_changes changes from the report changelog."""
    return _get_changelog(database, nr_changes, report_uuid=report_uuid)


@bottle.get("/api/v3/changelog/<nr_changes>", authentication_required=False)
def get_changelog(nr_changes: str, database: Database):
    """Return the recent most nr_changes changes from the changelog."""
    return _get_changelog(database, nr_changes)
