"""Changelog routes."""

from pymongo.database import Database
import bottle

from database import measurements, reports
from server_utilities.type import MetricId, ReportId, SourceId, SubjectId


def _get_changelog(database: Database, nr_changes: str, **uuids: str):
    """Return the recent most nr_changes changes from the changelog."""
    limit = int(nr_changes)
    changes = []
    if "report_uuid" in uuids:
        changes.extend(
            [dict(delta=change["delta"], timestamp=change["start"])
             for change in measurements.changelog(database, uuids["report_uuid"], limit)])
    changes.extend(
        [dict(delta=change["delta"]["description"], timestamp=change["timestamp"]) for change in
         reports.changelog(database, limit, **uuids) if "delta" in change])
    return dict(changelog=sorted(changes, reverse=True, key=lambda change: change["timestamp"])[:limit])


@bottle.get("/api/v1/changelog/report/<report_uuid>/source/<source_uuid>/<nr_changes>")
def get_source_changelog(report_uuid: ReportId, source_uuid: SourceId, nr_changes: str, database: Database):
    """Return the recent most nr_changes changes from the source changelog."""
    return _get_changelog(database, nr_changes, report_uuid=report_uuid, source_uuid=source_uuid)


@bottle.get("/api/v1/changelog/report/<report_uuid>/metric/<metric_uuid>/<nr_changes>")
def get_metric_changelog(report_uuid: ReportId, metric_uuid: MetricId, nr_changes: str, database: Database):
    """Return the recent most nr_changes changes from the metric changelog."""
    return _get_changelog(database, nr_changes, report_uuid=report_uuid, metric_uuid=metric_uuid)


@bottle.get("/api/v1/changelog/report/<report_uuid>/subject/<subject_uuid>/<nr_changes>")
def get_subject_changelog(report_uuid: ReportId, subject_uuid: SubjectId, nr_changes: str, database: Database):
    """Return the recent most nr_changes changes from the subject changelog."""
    return _get_changelog(database, nr_changes, report_uuid=report_uuid, subject_uuid=subject_uuid)


@bottle.get("/api/v1/changelog/report/<report_uuid>/<nr_changes>")
def get_report_changelog(report_uuid: ReportId, nr_changes: str, database: Database):
    """Return the recent most nr_changes changes from the report changelog."""
    return _get_changelog(database, nr_changes, report_uuid=report_uuid)


@bottle.get("/api/v1/changelog/<nr_changes>")
def get_changelog(nr_changes: str, database: Database):
    """Return the recent most nr_changes changes from the changelog."""
    return _get_changelog(database, nr_changes)
